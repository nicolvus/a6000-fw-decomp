## GetExtListTop @ 0x2c5b0 (DmmAccessPLA::GetExtListTop) bytes=8 sig=undefined __stdcall GetExtListTop(void * param_1)
```c
/* DmmAccessPLA::GetExtListTop(void*) */

int DmmAccessPLA::GetExtListTop(void *param_1)

{
  return (int)param_1 + 0x10;
}

```
asm:
0x2c5b0: push {r7,lr}
0x2c5b2: adds r0, #0x10
0x2c5b4: add r7, sp,#0x0
0x2c5b6: pop {r7,pc}
callees=[] callers=0 inc_refs=2

## GetUnitHandle @ 0x2c594 (DmmAccessPLA::GetUnitHandle) bytes=14 sig=undefined __stdcall GetUnitHandle(void * param_1)
```c
/* DmmAccessPLA::GetUnitHandle(void*) */

undefined2 DmmAccessPLA::GetUnitHandle(void *param_1)

{
  return *(undefined2 *)((int)param_1 + 4);
}

```
asm:
0x2c594: push {r7,lr}
0x2c596: add r7, sp,#0x0
0x2c598: ldrb r3, [r0,#0x4]
0x2c59a: ldrb r0, [r0,#0x5]
0x2c59c: orr.w r0, r3, r0, lsl #0x8
0x2c5a0: pop {r7,pc}
callees=[] callers=1 inc_refs=2

## GetExtSizeFromDmmAlloc @ 0x2c638 (DmmAccessPLA::GetExtSizeFromDmmAlloc) bytes=12 sig=undefined __stdcall GetExtSizeFromDmmAlloc(void * param_1, ushort param_2)
```c
/* DmmAccessPLA::GetExtSizeFromDmmAlloc(void*, unsigned short) */

undefined4 DmmAccessPLA::GetExtSizeFromDmmAlloc(void *param_1,ushort param_2)

{
  return *(undefined4 *)((int)param_1 + (uint)param_2 * 8 + 0x14);
}

```
asm:
0x2c638: add.w r1, r0, r1, lsl #0x3
0x2c63c: push {r7,lr}
0x2c63e: add r7, sp,#0x0
0x2c640: ldr r0, [r1,#0x14]
0x2c642: pop {r7,pc}
callees=[] callers=0 inc_refs=0

## SetExtListPackStatus @ 0x2c5ee (DmmAccessPLA::SetExtListPackStatus) bytes=16 sig=undefined __stdcall SetExtListPackStatus(void * param_1, uint param_2, ushort param_3, ushort param_4, uint param_5)
```c
/* DmmAccessPLA::SetExtListPackStatus(void*, unsigned int, unsigned short, unsigned short, unsigned
   int) */

void DmmAccessPLA::SetExtListPackStatus
               (void *param_1,uint param_2,ushort param_3,ushort param_4,uint param_5)

{
  *(ushort *)((int)param_1 + 8) = param_4;
  *(uint *)param_1 = param_2;
  *(uint *)((int)param_1 + 4) = (uint)param_3;
  *(uint *)((int)param_1 + 0xc) = param_5;
  return;
}

```
asm:
0x2c5ee: push {r7,lr}
0x2c5f0: add r7, sp,#0x0
0x2c5f2: strh r3, [r0,#0x8]
0x2c5f4: ldr r3, [r7,#0x8]
0x2c5f6: stm r0, {r1,r2}
0x2c5fa: str r3, [r0,#0xc]
0x2c5fc: pop {r7,pc}
callees=[] callers=1 inc_refs=2

## AllocDmmMemory @ 0x2bc9c (DmmAccess::AllocDmmMemory) bytes=132 sig=undefined __stdcall AllocDmmMemory(int param_1, ushort * param_2)
```c
/* DmmAccess::AllocDmmMemory(int, unsigned short*) */

undefined4 DmmAccess::AllocDmmMemory(int param_1,ushort *param_2)

{
  t_unitTypeConvertList *ptVar1;
  undefined4 uVar2;
  
  MprCtrlLog::SetStartApiLog(0x80,0x60b);
  ptVar1 = (t_unitTypeConvertList *)UnitTypeTableSelect(param_1);
  MprCtrlLog::SetMemoryMapLog(param_1);
  MonCtrl::ConPrintfMessage
            (mp_dbg,"[DmmAccess]AllocDmmMemory: AllocDmmMemory UnitTypeTableSelect(%d)=0x%x",param_1
             ,ptVar1);
  if (param_1 < 0x1a) {
    if (ptVar1 == (t_unitTypeConvertList *)0x0) {
      MonCtrl::ConPrintfMessage(mp_err,"[DmmAccess]AllocDmmMemory: memory table undefined.");
      uVar2 = 0;
    }
    else {
      uVar2 = GetDmmExtList(ptVar1,param_2);
      *(undefined4 *)(m_extPackHeaderAdrs + param_1 * 4) = uVar2;
    }
  }
  else {
    uVar2 = 0;
    MonCtrl::ConPrintfMessage(mp_err,"[DmmAccess]AllocDmmMemory: invalid modeId.");
  }
  MprCtrlLog::SetEndApiLog(0x80,0,0x623);
  return uVar2;
}

```
asm:
0x2bc9c: push {r4,r5,r6,r7,r8,lr}
0x2bca0: mov r5, r0
0x2bca2: add r7, sp,#0x0
0x2bca4: movs r0, #0x80
0x2bca6: mov r8, r1
0x2bca8: movw r1, #0x60b
0x2bcac: blx 0x0001f508
0x2bcb0: mov r0, r5
0x2bcb2: blx 0x0001f2a8
0x2bcb6: ldr r4, [0x0002bd20]
0x2bcb8: add r4, pc
0x2bcba: mov r6, r0
0x2bcbc: mov r0, r5
0x2bcbe: blx 0x0001f20c
0x2bcc2: ldr r3, [0x0002bd24]
0x2bcc4: ldr r1, [0x0002bd28]
0x2bcc6: mov r2, r5
0x2bcc8: ldr r3, [r4,r3]
0x2bcca: add r1, pc
0x2bccc: ldr r0, [r3,#0x0]
0x2bcce: mov r3, r6
0x2bcd0: blx 0x0001f860
0x2bcd4: cmp r5, #0x19
0x2bcd6: bgt 0x0002bcfe
0x2bcd8: cbz r6, 0x0002bcee
0x2bcda: mov r0, r6
0x2bcdc: mov r1, r8
0x2bcde: blx 0x0001eee8
0x2bce2: ldr r3, [0x0002bd2c]
0x2bce4: ldr r3, [r4,r3]
0x2bce6: mov r6, r0
0x2bce8: str.w r0, [r3,r5,lsl #0x2]
0x2bcec: b 0x0002bd0e
0x2bcee: ldr r3, [0x0002bd30]
0x2bcf0: ldr r1, [0x0002bd34]
0x2bcf2: ldr r3, [r4,r3]
0x2bcf4: add r1, pc
0x2bcf6: ldr r0, [r3,#0x0]
0x2bcf8: blx 0x0001f860
0x2bcfc: b 0x0002bd0e
0x2bcfe: ldr r3, [0x0002bd30]
0x2bd00: movs r6, #0x0
0x2bd02: ldr r1, [0x0002bd38]
0x2bd04: ldr r3, [r4,r3]
0x2bd06: add r1, pc
0x2bd08: ldr r0, [r3,#0x0]
0x2bd0a: blx 0x0001f860
0x2bd0e: movs r0, #0x80
0x2bd10: movs r1, #0x0
0x2bd12: movw r2, #0x623
0x2bd16: blx 0x0001eab0
0x2bd1a: mov r0, r6
0x2bd1c: pop.w {r4,r5,r6,r7,r8,pc}
callees=[('0x1eab0', 'MprCtrlLog::SetEndApiLog'), ('0x1eee8', 'DmmAccess::GetDmmExtList'), ('0x1f20c', 'MprCtrlLog::SetMemoryMapLog'), ('0x1f2a8', 'DmmAccess::UnitTypeTableSelect'), ('0x1f508', 'MprCtrlLog::SetStartApiLog'), ('0x1f860', '<EXTERNAL>::MonCtrl::ConPrintfMessage')] callers=1 inc_refs=2

## DmmCloseAndFree @ 0x2afe8 (DmmAccess::DmmCloseAndFree) bytes=32 sig=undefined __stdcall DmmCloseAndFree(ushort param_1)
```c
/* DmmAccess::DmmCloseAndFree(unsigned short) */

int DmmAccess::DmmCloseAndFree(ushort param_1)

{
  short sVar1;
  undefined2 *puVar2;
  int iVar3;
  undefined4 uVar4;
  char *pcVar5;
  int iVar6;
  uint uVar7;
  undefined4 uStack_30;
  undefined2 *apuStack_2c [4];
  
  MprCtrlLog::SetUnitHandleLog('y',param_1,0x389);
  uStack_30 = 0;
  apuStack_2c[0] = (undefined2 *)0x0;
  iVar3 = osal_dynamic_id(0x2a,199,&uStack_30);
  if (iVar3 != 0) {
    return 0;
  }
  uVar4 = osal_valloc_msg_wait(0x61003c,apuStack_2c,0x18,0);
  iVar3 = CheckOSALRetCode(uVar4,0);
  puVar2 = apuStack_2c[0];
  if (iVar3 == 0) {
    MonCtrl::ConPrintfMessage(mp_err,"[DmmAccess]DmmCloseORFree_body() osal_try_alloc_msg failed!");
    pcVar5 = mp_err;
    uVar4 = GetOSALRetMsg(uVar4);
    MonCtrl::ConPrintfMessage(pcVar5,"osal error msg(%s)",uVar4);
    iVar3 = 0;
  }
  else {
    memset(apuStack_2c[0],0,0x18);
    *puVar2 = 4;
    puVar2[1] = param_1;
    FUN_0002a9c2(apuStack_2c[0],uStack_30);
    puVar2[10] = 0;
    puVar2[0xb] = 2;
    MonCtrl::ConPrintfMessage
              (mp_dbg,"[DmmAccess]DmmCloseORFree_body() Message Send :unitHandle(%d) req_id(%d)",
               (uint)param_1,0);
    uVar4 = osal_snd_msg(0x61003c,apuStack_2c[0]);
    iVar3 = CheckOSALRetCode(uVar4,0);
    if (iVar3 == 0) {
      MonCtrl::ConPrintfMessage
                (mp_err,"[DmmAccess]DmmCloseORFree_body() osal_snd_msg failed! osal_err=0x%x",uVar4)
      ;
      pcVar5 = mp_err;
      uVar4 = GetOSALRetMsg(uVar4);
    }
    else {
      uVar4 = osal_rcv_msg_tmo(uStack_30,apuStack_2c,0xffffffff);
      iVar3 = CheckOSALRetCode(uVar4,0);
      puVar2 = apuStack_2c[0];
      if (iVar3 != 0) {
        sVar1 = apuStack_2c[0][1];
        iVar3 = CheckDMMRetCode(sVar1,(char *)0x0);
        pcVar5 = mp_dbg;
        if (iVar3 == 0) {
          MonCtrl::ConPrintfMessage
                    (mp_err,"[DmmAccess]DmmCloseORFree_body() CLOSE or FREE failed! dmm_err=0x%x",
                     (int)sVar1);
          pcVar5 = mp_err;
          uVar4 = GetDMMRetMsg(sVar1);
          MonCtrl::ConPrintfMessage(pcVar5,"osal error msg(%s)",uVar4);
          MprCtrlLog::SetErrLog(0x8a,(int)sVar1,0x3e2,"DmmAccess.cpp");
          iVar3 = 0;
        }
        else {
          uVar4 = GetDMMRetMsg(sVar1);
          MonCtrl::ConPrintfMessage
                    (pcVar5,"[DmmAccess]DmmCloseORFree_body() CLOSE or FREE (%s) req_id(%d)",uVar4,
                     (uint)(ushort)puVar2[3]);
          uVar7 = (uint)(ushort)puVar2[3];
          iVar3 = 1 - uVar7;
          if (1 < uVar7) {
            iVar3 = 0;
          }
        }
        iVar6 = osal_free_msg(uStack_30,apuStack_2c[0]);
        if (iVar6 != 0) {
          iVar3 = 0;
          MonCtrl::ConPrintfMessage
                    (mp_err,"[DmmAccess]DmmCloseORFree_body() osal_free_msg failed! osal_err=0x%x",
                     iVar6);
          pcVar5 = mp_err;
          uVar4 = GetOSALRetMsg(iVar6);
          MonCtrl::ConPrintfMessage(pcVar5,"osal error msg(%s)",uVar4);
        }
        goto LAB_0002af6e;
      }
      MonCtrl::ConPrintfMessage
                (mp_err,"[DmmAccess]DmmCloseORFree_body() osal_rcv_msg failed! osal_err=0x%x",uVar4)
      ;
      pcVar5 = mp_err;
      uVar4 = GetOSALRetMsg(uVar4);
    }
    iVar3 = 0;
    MonCtrl::ConPrintfMessage(pcVar5,"osal error msg(%s)",uVar4);
  }
LAB_0002af6e:
  osal_dynamic_id(0x4a,0,uStack_30);
  return iVar3;
}

```
asm:
0x2afe8: push {r4,r5,r7,lr}
0x2afea: mov r4, r0
0x2afec: mov r1, r4
0x2afee: movs r0, #0x79
0x2aff0: add r7, sp,#0x0
0x2aff2: movw r2, #0x389
0x2aff6: blx 0x0001ee80
0x2affa: mov r0, r4
0x2affc: movs r1, #0x4
0x2affe: movs r2, #0x2
0x2b000: pop.w {r4,r5,r7,lr}
0x2b004: b.w 0x0001fca0
callees=[('0x1ee80', 'MprCtrlLog::SetUnitHandleLog')] callers=1 inc_refs=2

## DmmAllocateNEWAndOpen_body @ 0x2b028 (DmmAccess::DmmAllocateNEWAndOpen_body) bytes=846 sig=undefined __stdcall DmmAllocateNEWAndOpen_body(uint param_1, ushort param_2, ushort param_3, ushort param_4)
```c
/* DmmAccess::DmmAllocateNEWAndOpen_body(unsigned int, unsigned short, unsigned short, unsigned
   short) */

void * DmmAccess::DmmAllocateNEWAndOpen_body
                 (uint param_1,ushort param_2,ushort param_3,ushort param_4)

{
  short sVar1;
  bool bVar2;
  short *psVar3;
  char *pcVar4;
  int iVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  uint uVar8;
  void *__dest;
  size_t __size;
  undefined4 local_30;
  short *local_2c [2];
  
  local_30 = 0;
  local_2c[0] = (short *)0x0;
  iVar5 = osal_dynamic_id(0x2a,199,&local_30);
  if (iVar5 != 0) {
    return (void *)0x0;
  }
  MonCtrl::ConPrintfMessage(mp_dbg,"[DmmAccess]DmmAllocateNEWAndOpen_body() req_id=%d",0);
  iVar5 = osal_valloc_msg_wait(0x61003c,local_2c,0x18,0);
  MonCtrl::ConPrintfMessage
            (mp_dbg,"[DmmAccess]DmmAllocateNEWAndOpen_body() OSAL ALLOC osalHandle=0x%09x",
             local_2c[0]);
  psVar3 = local_2c[0];
  if (iVar5 != 0) {
    MonCtrl::ConPrintfMessage
              (mp_err,"[DmmAccess]DmmAllocateNEWAndOpen_body() OSAL ALLOC ERROR osal_err=%d",iVar5);
    pcVar4 = mp_err;
    uVar6 = GetOSALRetMsg(iVar5);
    MonCtrl::ConPrintfMessage(pcVar4,"osal error msg (%s)",uVar6);
    bVar2 = false;
    goto LAB_0002b1c4;
  }
  memset(local_2c[0],0,0x18);
  switch((uint)param_3) {
  case 1:
    memset(psVar3,0,0x18);
    *psVar3 = 1;
    *(uint *)(psVar3 + 2) = param_1;
    psVar3[6] = -1;
    psVar3[7] = -1;
    FUN_0002a9c2(local_2c[0],local_30);
    psVar3[10] = 0;
    break;
  case 2:
    memset(psVar3,0,0x18);
    *(uint *)(psVar3 + 2) = param_1;
    *psVar3 = 2;
    psVar3[1] = param_2;
    goto LAB_0002b15a;
  case 3:
    memset(psVar3,0,0x18);
    *psVar3 = 3;
    *(uint *)(psVar3 + 2) = param_1;
    psVar3[1] = param_2;
    psVar3[6] = -1;
    psVar3[7] = -1;
    FUN_0002a9c2(local_2c[0],local_30);
    psVar3[10] = 0;
    break;
  default:
    bVar2 = false;
    MonCtrl::ConPrintfMessage
              (mp_err,"[DmmAccess]DmmAllocateNEWAndOpen_body() msg_id select failed (0x%08x)",
               (uint)param_3);
    goto LAB_0002b17a;
  case 5:
    memset(psVar3,0,0x18);
    *psVar3 = 5;
    psVar3[1] = param_2;
    psVar3[6] = -1;
    psVar3[7] = -1;
LAB_0002b15a:
    FUN_0002a9c2(local_2c[0],local_30);
    psVar3[10] = 0;
  }
  psVar3[0xb] = param_4;
  bVar2 = true;
LAB_0002b17a:
  MonCtrl::ConPrintfMessage(mp_dbg,"[DmmAccess]DmmAllocateNEWAndOpen_body() OSAL ALLOC MessageMADE")
  ;
  if (bVar2) {
    iVar5 = osal_snd_msg(0x61003c,local_2c[0]);
    if (iVar5 == 0) {
      MonCtrl::ConPrintfMessage
                (mp_dbg,"[DmmAccess]DmmAllocateNEWAndOpen_body() OSAL osal_snd_msg success!------");
    }
    else {
      MonCtrl::ConPrintfMessage
                (mp_err,
                 "[DmmAccess]DmmAllocateNEWAndOpen_body() OSAL osal_snd_msg ERROR! osal_err=%d",
                 iVar5);
      pcVar4 = mp_err;
      uVar6 = GetOSALRetMsg(iVar5);
      MonCtrl::ConPrintfMessage(pcVar4,"osal error msg(%s)\r\n",uVar6);
      bVar2 = false;
    }
  }
LAB_0002b1c4:
  MonCtrl::ConPrintfMessage(mp_dbg,"[DmmAccess]DmmAllocateNEWAndOpen_body() OSAL RCV STRAT");
  uVar6 = local_30;
  __dest = (void *)0x0;
  if (!bVar2) goto LAB_0002b3cc;
  MonCtrl::ConPrintfMessage
            (mp_dbg,"[DmmAccess]DmmAllocateNEWAndOpen_body() OSAL osal_rcv_msg start!");
  iVar5 = osal_rcv_msg_tmo(local_30,local_2c,0xffffffff);
  if (iVar5 == 0) {
    MonCtrl::ConPrintfMessage
              (mp_dbg,
               "[DmmAccess]DmmAllocateNEWAndOpen_body() OSAL osal_rcv_msg recevied! res_que=%d",
               uVar6);
    psVar3 = local_2c[0];
    sVar1 = *local_2c[0];
    if ((((sVar1 == -0x7fff) || (sVar1 == -0x7ffb)) || (sVar1 == -0x7ffd)) || (sVar1 == -0x7ffe)) {
      sVar1 = local_2c[0][1];
      iVar5 = CheckDMMRetCode(sVar1,(char *)0x0);
      pcVar4 = mp_dbg;
      if (iVar5 == 0) {
        MonCtrl::ConPrintfMessage
                  (mp_err,"[DmmAccess]DmmAllocateNEWAndOpen_body() CompBase.ret_code (0x%x)",
                   (int)sVar1);
        pcVar4 = mp_err;
        uVar7 = GetDMMRetMsg(sVar1);
        MonCtrl::ConPrintfMessage(pcVar4,"dmm error msg(%s)\r\n",uVar7);
        MprCtrlLog::SetErrLog(0x89,(int)sVar1,0x326,"DmmAccess.cpp");
        __dest = (void *)0x0;
      }
      else {
        uVar7 = GetDMMRetMsg(sVar1);
        MonCtrl::ConPrintfMessage
                  (pcVar4,"[DmmAccess]DmmAllocateNEWAndOpen_body()  dmm msg(%s)",uVar7);
        uVar8 = (uint)(ushort)psVar3[4];
        MonCtrl::ConPrintfMessage
                  (mp_dbg,"[DmmAccess]DmmAllocateNEWAndOpen_body() OSAL rcv    extCount=%d",uVar8);
        MonCtrl::ConPrintfMessage
                  (mp_dbg,"[DmmAccess]DmmAllocateNEWAndOpen_body() OSAL rcv    req_id=%d",
                   (uint)(ushort)psVar3[3]);
        MonCtrl::ConPrintfMessage
                  (mp_dbg,"[DmmAccess]DmmAllocateNEWAndOpen_body() OSAL rcv    unitHandle=%d",
                   (uint)(ushort)psVar3[2]);
        if (uVar8 == 0) {
          __size = 0x18;
        }
        else {
          __size = (uVar8 + 2) * 8;
        }
        __dest = malloc(__size);
        memcpy(__dest,psVar3,__size);
        MonCtrl::ConPrintfMessage
                  (mp_dbg,
                   "[DmmAccess]DmmAllocateNEWAndOpen_body() OSAL rcv malloc p_tmpPack=0x%08x size=%d,line%d"
                   ,__dest,__size,0x321);
      }
    }
    else {
      MonCtrl::ConPrintfMessage
                (mp_err,
                 "[DmmAccess]DmmAllocateNEWAndOpen_body() osal_work_comp->CompBase.msg_id ILLIGAL (%d)"
                );
      __dest = (void *)0x0;
    }
    iVar5 = osal_free_msg(uVar6,local_2c[0]);
    if (iVar5 == 0) goto LAB_0002b3cc;
    MonCtrl::ConPrintfMessage(mp_err,"osal_free_msg err(0x%x)",iVar5);
    pcVar4 = mp_err;
    uVar6 = GetOSALRetMsg(iVar5);
    MonCtrl::ConPrintfMessage(pcVar4,"osal error msg(%s)",uVar6);
    if (__dest == (void *)0x0) goto LAB_0002b3cc;
    MonCtrl::ConPrintfMessage(mp_dbg,"[DmmAccess]DmmAllocateNEWAndOpen_body() free(0x%08x)",__dest);
    free(__dest);
  }
  else {
    MonCtrl::ConPrintfMessage
              (mp_err,"[DmmAccess]DmmAllocateNEWAndOpen_body() OSAL osal_rcv_msg ERROR! osal_err=%d"
               ,iVar5);
    pcVar4 = mp_err;
    uVar6 = GetOSALRetMsg(iVar5);
    MonCtrl::ConPrintfMessage(pcVar4,"osal error msg(%s)\r\n",uVar6);
  }
  __dest = (void *)0x0;
LAB_0002b3cc:
  osal_dynamic_id(0x4a,0,local_30);
  return __dest;
}

```
asm:
0x2b028: push {r4,r5,r6,r7,r8,r9,r10,r11,lr}
0x2b02c: sub sp, #0x1c
0x2b02e: add r7, sp,#0x8
0x2b030: movs r4, #0x0
0x2b032: mov r10, r0
0x2b034: str r2, [r7,#0x4]
0x2b036: add.w r2, r7, #0x10
0x2b03a: mov r11, r1
0x2b03c: movs r0, #0x2a
0x2b03e: str.w r4, [r2,#-0x8]!
0x2b042: movs r1, #0xc7
0x2b044: mov r8, r3
0x2b046: str r4, [r7,#0xc]
0x2b048: blx 0x0001fb3c
0x2b04c: ldr r5, [0x0002b314]
0x2b04e: add r5, pc
0x2b050: mov r6, r0
0x2b052: cmp r0, #0x0
0x2b054: bne.w 0x0002b3d8
0x2b058: ldr r3, [0x0002b318]
0x2b05a: mov r2, r6
0x2b05c: ldr r1, [0x0002b31c]
0x2b05e: ldr r4, [r5,r3]
0x2b060: add r1, pc
0x2b062: ldr r0, [r4,#0x0]
0x2b064: blx 0x0001f860
0x2b068: add.w r1, r7, #0xc
0x2b06c: movs r2, #0x18
0x2b06e: ldr r0, [0x0002b310]
0x2b070: mov r3, r6
0x2b072: blx 0x0001f2f4
0x2b076: ldr r1, [0x0002b320]
0x2b078: ldr r2, [r7,#0xc]
0x2b07a: add r1, pc
0x2b07c: mov r9, r0
0x2b07e: ldr r0, [r4,#0x0]
0x2b080: blx 0x0001f860
0x2b084: cmp.w r9, #0x0
0x2b088: beq 0x0002b0b6
0x2b08a: ldr r3, [0x0002b324]
0x2b08c: mov r2, r9
0x2b08e: ldr r1, [0x0002b328]
0x2b090: ldr.w r8, r5, r3
0x2b094: add r1, pc
0x2b096: ldr.w r0, [r8,#0x0]
0x2b09a: blx 0x0001f860
0x2b09e: mov r0, r9
0x2b0a0: ldr.w r8, [r8,#0x0]
0x2b0a4: blx 0x0001f740
0x2b0a8: ldr r1, [0x0002b32c]
0x2b0aa: add r1, pc
0x2b0ac: mov r2, r0
0x2b0ae: mov r0, r8
0x2b0b0: blx 0x0001f860
0x2b0b4: b 0x0002b1c4
0x2b0b6: ldr r6, [r7,#0xc]
0x2b0b8: mov r1, r9
0x2b0ba: movs r2, #0x18
0x2b0bc: mov r0, r6
0x2b0be: blx 0x0001ee5c
0x2b0c2: ldr r1, [r7,#0x4]
0x2b0c4: subs r3, r1, #0x1
0x2b0c6: cmp r3, #0x4
0x2b0c8: bhi 0x0002b168
0x2b0ca: tbb [pc,r3]
0x2b0d4: movs r2, #0x18
0x2b0d6: mov r0, r6
0x2b0d8: movs r1, #0x0
0x2b0da: blx 0x0001ee5c
0x2b0de: movs r2, #0x5
0x2b0e0: mov.w r3, #0xffffffff
0x2b0e4: strh r2, [r6,#0x0]
0x2b0e6: strh.w r11, [r6,#0x2]
0x2b0ea: str r3, [r6,#0xc]
0x2b0ec: b 0x0002b15a
0x2b0ee: movs r2, #0x18
0x2b0f0: movs r1, #0x0
0x2b0f2: mov r0, r6
0x2b0f4: blx 0x0001ee5c
0x2b0f8: movs r1, #0x1
0x2b0fa: mov.w r3, #0xffffffff
0x2b0fe: strh r1, [r6,#0x0]
0x2b100: str.w r10, [r6,#0x4]
0x2b104: str r3, [r6,#0xc]
0x2b106: ldr r0, [r7,#0xc]
0x2b108: ldr r1, [r7,#0x8]
0x2b10a: bl 0x0002a9c2
0x2b10e: movs r2, #0x0
0x2b110: strh r2, [r6,#0x14]
0x2b112: strh.w r8, [r6,#0x16]
0x2b116: movs r6, #0x1
0x2b118: b 0x0002b17a
0x2b11a: movs r1, #0x0
0x2b11c: movs r2, #0x18
0x2b11e: mov r0, r6
0x2b120: blx 0x0001ee5c
0x2b124: movs r3, #0x3
0x2b126: ldr r1, [r7,#0x8]
0x2b128: strh r3, [r6,#0x0]
0x2b12a: mov.w r3, #0xffffffff
0x2b12e: str.w r10, [r6,#0x4]
0x2b132: strh.w r11, [r6,#0x2]
0x2b136: str r3, [r6,#0xc]
0x2b138: ldr r0, [r7,#0xc]
0x2b13a: bl 0x0002a9c2
0x2b13e: movs r1, #0x0
0x2b140: strh r1, [r6,#0x14]
0x2b142: b 0x0002b112
0x2b144: movs r2, #0x18
0x2b146: mov r0, r6
0x2b148: movs r1, #0x0
0x2b14a: blx 0x0001ee5c
0x2b14e: movs r2, #0x2
0x2b150: str.w r10, [r6,#0x4]
0x2b154: strh r2, [r6,#0x0]
0x2b156: strh.w r11, [r6,#0x2]
0x2b15a: ldr r0, [r7,#0xc]
0x2b15c: ldr r1, [r7,#0x8]
0x2b15e: bl 0x0002a9c2
0x2b162: movs r3, #0x0
0x2b164: strh r3, [r6,#0x14]
0x2b166: b 0x0002b112
0x2b168: ldr r3, [0x0002b324]
0x2b16a: movs r6, #0x0
0x2b16c: ldr r1, [0x0002b330]
0x2b16e: ldr r2, [r7,#0x4]
0x2b170: ldr r3, [r5,r3]
0x2b172: add r1, pc
0x2b174: ldr r0, [r3,#0x0]
0x2b176: blx 0x0001f860
0x2b17a: ldr r1, [0x0002b334]
0x2b17c: ldr r0, [r4,#0x0]
0x2b17e: add r1, pc
0x2b180: blx 0x0001f860
0x2b184: cbz r6, 0x0002b1c4
0x2b186: ldr r0, [0x0002b310]
0x2b188: ldr r1, [r7,#0xc]
0x2b18a: blx 0x0001f460
0x2b18e: mov r8, r0
0x2b190: cbz r0, 0x0002b1ba
0x2b192: ldr r3, [0x0002b324]
0x2b194: mov r2, r8
0x2b196: ldr r1, [0x0002b338]
0x2b198: ldr r6, [r5,r3]
0x2b19a: add r1, pc
0x2b19c: ldr r0, [r6,#0x0]
0x2b19e: blx 0x0001f860
0x2b1a2: mov r0, r8
0x2b1a4: ldr r6, [r6,#0x0]
0x2b1a6: blx 0x0001f740
0x2b1aa: ldr r1, [0x0002b33c]
0x2b1ac: add r1, pc
0x2b1ae: mov r2, r0
0x2b1b0: mov r0, r6
0x2b1b2: blx 0x0001f860
0x2b1b6: movs r6, #0x0
0x2b1b8: b 0x0002b1c4
0x2b1ba: ldr r1, [0x0002b340]
0x2b1bc: ldr r0, [r4,#0x0]
0x2b1be: add r1, pc
0x2b1c0: blx 0x0001f860
0x2b1c4: ldr r1, [0x0002b344]
0x2b1c6: ldr r0, [r4,#0x0]
0x2b1c8: add r1, pc
0x2b1ca: blx 0x0001f860
0x2b1ce: ldr.w r10, [r7,#0x8]
0x2b1d2: cmp r6, #0x0
0x2b1d4: beq.w 0x0002b3cc
0x2b1d8: ldr r1, [0x0002b348]
0x2b1da: ldr r0, [r4,#0x0]
0x2b1dc: add r1, pc
0x2b1de: blx 0x0001f860
0x2b1e2: ldr r0, [r7,#0x8]
0x2b1e4: add.w r1, r7, #0xc
0x2b1e8: mov.w r2, #0xffffffff
0x2b1ec: blx 0x0001f1b4
0x2b1f0: mov r6, r0
0x2b1f2: cbz r0, 0x0002b21a
0x2b1f4: ldr r3, [0x0002b324]
0x2b1f6: mov r2, r6
0x2b1f8: ldr r1, [0x0002b34c]
0x2b1fa: ldr r4, [r5,r3]
0x2b1fc: add r1, pc
0x2b1fe: ldr r0, [r4,#0x0]
0x2b200: blx 0x0001f860
0x2b204: mov r0, r6
0x2b206: ldr r4, [r4,#0x0]
0x2b208: blx 0x0001f740
0x2b20c: ldr r1, [0x0002b350]
0x2b20e: add r1, pc
0x2b210: mov r2, r0
0x2b212: mov r0, r4
0x2b214: blx 0x0001f860
0x2b218: b 0x0002b3ca
0x2b21a: ldr r1, [0x0002b354]
0x2b21c: mov r2, r10
0x2b21e: ldr r0, [r4,#0x0]
0x2b220: add r1, pc
0x2b222: blx 0x0001f860
0x2b226: ldr.w r8, [r7,#0xc]
0x2b22a: movw r3, #0x8001
0x2b22e: ldrh.w r2, [r8,#0x0]
0x2b232: cmp r2, r3
0x2b234: beq 0x0002b24a
0x2b236: adds r3, #0x4
0x2b238: cmp r2, r3
0x2b23a: beq 0x0002b24a
0x2b23c: subs r3, #0x2
0x2b23e: cmp r2, r3
0x2b240: beq 0x0002b24a
0x2b242: subs r3, #0x1
0x2b244: cmp r2, r3
0x2b246: bne.w 0x0002b378
0x2b24a: ldrsh.w r9, [r8,#0x2]
0x2b24e: movs r1, #0x0
0x2b250: mov r0, r9
0x2b252: blx 0x0001f7bc
0x2b256: mov r6, r0
0x2b258: cmp r0, #0x0
0x2b25a: beq 0x0002b2d2
0x2b25c: mov r0, r9
0x2b25e: ldr r6, [r4,#0x0]
0x2b260: blx 0x0001eac8
0x2b264: ldr r1, [0x0002b358]
0x2b266: add r1, pc
0x2b268: mov r2, r0
0x2b26a: mov r0, r6
0x2b26c: blx 0x0001f860
0x2b270: ldrh.w r6, [r8,#0x8]
0x2b274: ldr r1, [0x0002b35c]
0x2b276: ldr r0, [r4,#0x0]
0x2b278: mov r2, r6
0x2b27a: add r1, pc
0x2b27c: blx 0x0001f860
0x2b280: ldr r1, [0x0002b360]
0x2b282: ldr r0, [r4,#0x0]
0x2b284: add r1, pc
0x2b286: ldrh.w r2, [r8,#0x6]
0x2b28a: blx 0x0001f860
0x2b28e: ldr r1, [0x0002b364]
0x2b290: ldr r0, [r4,#0x0]
0x2b292: add r1, pc
0x2b294: ldrh.w r2, [r8,#0x4]
0x2b298: blx 0x0001f860
0x2b29c: cbz r6, 0x0002b2a8
0x2b29e: add.w r9, r6, #0x2
0x2b2a2: lsl.w r9, r9, #0x3
0x2b2a6: b 0x0002b2ac
0x2b2a8: mov.w r9, #0x18
0x2b2ac: mov r0, r9
0x2b2ae: blx 0x0001f764
0x2b2b2: mov r1, r8
0x2b2b4: mov r2, r9
0x2b2b6: mov r6, r0
0x2b2b8: blx 0x0001f304
0x2b2bc: ldr r1, [0x0002b368]
0x2b2be: movw r3, #0x321
0x2b2c2: mov r2, r6
0x2b2c4: str r3, [sp,#0x0]
0x2b2c6: add r1, pc
0x2b2c8: ldr r0, [r4,#0x0]
0x2b2ca: mov r3, r9
0x2b2cc: blx 0x0001f860
0x2b2d0: b 0x0002b386
0x2b2d2: ldr r3, [0x0002b324]
0x2b2d4: mov r2, r9
0x2b2d6: ldr r1, [0x0002b36c]
0x2b2d8: ldr.w r8, r5, r3
0x2b2dc: add r1, pc
0x2b2de: ldr.w r0, [r8,#0x0]
0x2b2e2: blx 0x0001f860
0x2b2e6: mov r0, r9
0x2b2e8: ldr.w r8, [r8,#0x0]
0x2b2ec: blx 0x0001eac8
0x2b2f0: ldr r1, [0x0002b370]
0x2b2f2: add r1, pc
0x2b2f4: mov r2, r0
0x2b2f6: mov r0, r8
0x2b2f8: blx 0x0001f860
0x2b2fc: ldr r3, [0x0002b374]
0x2b2fe: movs r0, #0x89
0x2b300: mov r1, r9
0x2b302: movw r2, #0x326
0x2b306: add r3, pc
0x2b308: blx 0x0001eba4
0x2b30c: b 0x0002b386
0x2b378: ldr r3, [0x0002b3e8]
0x2b37a: ldr r1, [0x0002b3ec]
0x2b37c: ldr r3, [r5,r3]
0x2b37e: add r1, pc
0x2b380: ldr r0, [r3,#0x0]
0x2b382: blx 0x0001f860
0x2b386: mov r0, r10
0x2b388: ldr r1, [r7,#0xc]
0x2b38a: blx 0x0001ff20
0x2b38e: mov r8, r0
0x2b390: cbz r0, 0x0002b3cc
0x2b392: ldr r3, [0x0002b3e8]
0x2b394: mov r2, r8
0x2b396: ldr r1, [0x0002b3f0]
0x2b398: ldr r5, [r5,r3]
0x2b39a: add r1, pc
0x2b39c: ldr r0, [r5,#0x0]
0x2b39e: blx 0x0001f860
0x2b3a2: mov r0, r8
0x2b3a4: ldr r5, [r5,#0x0]
0x2b3a6: blx 0x0001f740
0x2b3aa: ldr r1, [0x0002b3f4]
0x2b3ac: add r1, pc
0x2b3ae: mov r2, r0
0x2b3b0: mov r0, r5
0x2b3b2: blx 0x0001f860
0x2b3b6: cbz r6, 0x0002b3cc
0x2b3b8: ldr r1, [0x0002b3f8]
0x2b3ba: mov r2, r6
0x2b3bc: ldr r0, [r4,#0x0]
0x2b3be: add r1, pc
0x2b3c0: blx 0x0001f860
0x2b3c4: mov r0, r6
0x2b3c6: blx 0x0001f0a4
0x2b3ca: movs r6, #0x0
0x2b3cc: movs r0, #0x4a
0x2b3ce: movs r1, #0x0
0x2b3d0: ldr r2, [r7,#0x8]
0x2b3d2: blx 0x0001fb3c
0x2b3d6: b 0x0002b3da
0x2b3d8: mov r6, r4
0x2b3da: mov r0, r6
0x2b3dc: add.w r7, r7, #0x14
0x2b3e0: mov sp, r7
0x2b3e2: pop.w {r4,r5,r6,r7,r8,r9,r10,r11,pc}
callees=[('0x1eac8', 'DmmAccess::GetDMMRetMsg'), ('0x1eba4', 'MprCtrlLog::SetErrLog'), ('0x1ee5c', '<EXTERNAL>::memset'), ('0x1f0a4', '<EXTERNAL>::free'), ('0x1f1b4', '<EXTERNAL>::osal_rcv_msg_tmo'), ('0x1f2f4', '<EXTERNAL>::osal_valloc_msg_wait'), ('0x1f304', '<EXTERNAL>::memcpy'), ('0x1f460', '<EXTERNAL>::osal_snd_msg'), ('0x1f740', 'DmmAccess::GetOSALRetMsg'), ('0x1f764', '<EXTERNAL>::malloc'), ('0x1f7bc', 'DmmAccess::CheckDMMRetCode'), ('0x1f860', '<EXTERNAL>::MonCtrl::ConPrintfMessage'), ('0x1fb3c', '<EXTERNAL>::osal_dynamic_id'), ('0x1ff20', '<EXTERNAL>::osal_free_msg'), ('0x2a9c2', 'FUN_0002a9c2')] callers=1 inc_refs=2

## CtrlAllocDmmMemory @ 0x245d0 (MprCtrlMcmd::CtrlAllocDmmMemory) bytes=64 sig=undefined __stdcall CtrlAllocDmmMemory(int param_1, char * * param_2)
```c
/* MprCtrlMcmd::CtrlAllocDmmMemory(int, char**) */

undefined4 MprCtrlMcmd::CtrlAllocDmmMemory(int param_1,char **param_2)

{
  int iVar1;
  undefined4 uVar2;
  ushort auStack_12 [3];
  
  if (param_1 < 2) {
    MonCtrl::ConPutStr(mp_msg);
  }
  else {
    iVar1 = StrUtil::StrHexToUInt32(param_2[1]);
    uVar2 = DmmAccess::AllocDmmMemory(iVar1,auStack_12);
    MonCtrl::ConPrintf(mp_msg,"ExtentList Addr(virtual): %x\n",uVar2);
  }
  return 1;
}

```
asm:
0x245d0: ldr r3, [0x00024610]
0x245d2: cmp r0, #0x1
0x245d4: push {r4,r7,lr}
0x245d6: sub sp, #0xc
0x245d8: ldr r2, [0x00024614]
0x245da: add r3, pc
0x245dc: add r7, sp,#0x0
0x245de: ldr r4, [r3,r2]
0x245e0: bgt 0x000245ee
0x245e2: ldr r1, [0x00024618]
0x245e4: ldr r0, [r4,#0x0]
0x245e6: add r1, pc
0x245e8: blx 0x0001f044
0x245ec: b 0x00024606
0x245ee: ldr r0, [r1,#0x4]
0x245f0: blx 0x0001ea00
0x245f4: adds r1, r7, #0x6
0x245f6: blx 0x0001fe1c
0x245fa: ldr r1, [0x0002461c]
0x245fc: add r1, pc
0x245fe: mov r2, r0
0x24600: ldr r0, [r4,#0x0]
0x24602: blx 0x0001ebb0
0x24606: movs r0, #0x1
0x24608: add.w r7, r7, #0xc
0x2460c: mov sp, r7
0x2460e: pop {r4,r7,pc}
callees=[('0x1ea00', '<EXTERNAL>::StrUtil::StrHexToUInt32'), ('0x1ebb0', '<EXTERNAL>::MonCtrl::ConPrintf'), ('0x1f044', '<EXTERNAL>::MonCtrl::ConPutStr'), ('0x1fe1c', 'DmmAccess::AllocDmmMemory')] callers=0 inc_refs=0
