/* S37: static analysis only. */

/* 0001e9c8 */

int _init(EVP_PKEY_CTX *ctx)

{
  int iVar1;
  
  iVar1 = entry(ctx);
  return iVar1;
}


/* 0001e9e8 */

void MprCtrlLog::CnvFileNameToId(char *param_1)

{
  (*(code *)PTR_CnvFileNameToId_0004bc74)(param_1);
  return;
}


/* 0001e9f4 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MprIf::NewFlashAviMMgr(FlashAviCreateParam *param_1,ulong *param_2)

{
  (*(code *)PTR_NewFlashAviMMgr_0004bc78)(param_1);
  return;
}


/* 0001ea00 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void StrUtil::StrHexToUInt32(char *param_1)

{
  (*(code *)PTR_StrHexToUInt32_0004bc7c)(param_1);
  return;
}


/* 0001ea0c */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int open(char *__file,int __oflag,...)

{
  int iVar1;
  
  iVar1 = (*(code *)PTR_open_0004bc80)(__file);
  return iVar1;
}


/* 0001ea18 */

void MprCtrl::GetStillSize(ushort param_1,ushort param_2,StillSize *param_3)

{
  (*(code *)PTR_GetStillSize_0004bc84)(param_1,param_2);
  return;
}


/* 0001ea24 */

void StateMgr::CallFunc(_FuncEntry *param_1,ObjMsg *param_2)

{
  (*(code *)PTR_CallFunc_0004bc88)(param_1);
  return;
}


/* 0001ea30 */

void MprCnv::Exchg_ExifSrcInfo(ExifSrcInfo *param_1,ExifSrcInfo *param_2)

{
  (*(code *)PTR_Exchg_ExifSrcInfo_0004bc8c)(param_1);
  return;
}


/* 0001ea40 */

void __thiscall MprCtrlInputEvent::ResetEvent(MprCtrlInputEvent *this)

{
  (*(code *)PTR_ResetEvent_0004bc90)(this);
  return;
}


/* 0001ea4c */

void __thiscall MWF::EventWrapper::EventWrapper(EventWrapper *this)

{
  (*(code *)PTR_EventWrapper_0004bc94)(this);
  return;
}


/* 0001ea58 */

void MprCtrl::GetEventSwitcherInstance(void)

{
  (*(code *)PTR_GetEventSwitcherInstance_0004bc98)();
  return;
}


/* 0001ea64 */

void UtilStillSize::CnvPbCapSize(int param_1)

{
  (*(code *)PTR_CnvPbCapSize_0004bc9c)(param_1);
  return;
}


/* 0001ea70 */

void __thiscall CapIdWrapper::~CapIdWrapper(CapIdWrapper *this)

{
  (*(code *)PTR__CapIdWrapper_0004bca0)(this);
  return;
}


/* 0001ea7c */

void UtilStillSize::CnvMovieAspect(int param_1)

{
  (*(code *)PTR_CnvMovieAspect_0004bca4)(param_1);
  return;
}


/* 0001ea88 */

void DmmAccess::DmmShareAndOpen(uint param_1,ushort param_2)

{
  (*(code *)PTR_DmmShareAndOpen_0004bca8)(param_1,param_2);
  return;
}


/* 0001ea94 */

void MprCnv::Exchg_LocalTime(LocalTime *param_1,T_LTM *param_2)

{
  (*(code *)PTR_Exchg_LocalTime_0004bcac)(param_1);
  return;
}


/* 0001eaa0 */

void StateMgr::CheckFunc(_FuncEntry *param_1,ObjMsg *param_2)

{
  (*(code *)PTR_CheckFunc_0004bcb0)(param_1);
  return;
}


/* 0001eab0 */

void MprCtrlLog::SetEndApiLog(uchar param_1,uint param_2,ushort param_3)

{
  (*(code *)PTR_SetEndApiLog_0004bcb4)(param_1,param_2,param_3);
  return;
}


/* 0001eabc */

void StatMgr::GetNextState(_FuncEntry *param_1,int param_2)

{
  (*(code *)PTR_GetNextState_0004bcb8)(param_1);
  return;
}


/* 0001eac8 */

void DmmAccess::GetDMMRetMsg(short param_1)

{
  (*(code *)PTR_GetDMMRetMsg_0004bcbc)((int)param_1);
  return;
}


/* 0001ead4 */

void __thiscall MprCtrlStillMgr::GetStillSizeRow(MprCtrlStillMgr *this,uint param_1)

{
  (*(code *)PTR_GetStillSizeRow_0004bcc0)(this);
  return;
}


/* 0001eae0 */

void MprCtrl::Init(void)

{
  (*(code *)PTR_Init_0004bcc4)();
  return;
}


/* 0001eaec */

void __thiscall MWF::EventReceiver::EventReceiver(EventReceiver *this)

{
  (*(code *)PTR_EventReceiver_0004bcc8)(this);
  return;
}


/* 0001eaf8 */

void __thiscall
MprCtrlStillMgr::GetStillRecInfo
          (MprCtrlStillMgr *this,StillSizeInfo *param_1,int *param_2,int *param_3,uint *param_4)

{
  (*(code *)PTR_GetStillRecInfo_0004bccc)(this);
  return;
}


/* 0001eb04 */

void __thiscall MprCtrl::_RecLineTable::GetMediaId(_RecLineTable *this,uint param_1)

{
  (*(code *)PTR_GetMediaId_0004bcd0)(this);
  return;
}


/* 0001eb10 */

void MprObjectUtil::MwfInt64(ObjMsg *param_1,uint param_2)

{
  (*(code *)PTR_MwfInt64_0004bcd4)(param_1);
  return;
}


/* 0001eb1c */

void MprCnv::Exchg_DevelopSrcInfo(DevelopSrcInfo *param_1,DevelopSrcInfo *param_2)

{
  (*(code *)PTR_Exchg_DevelopSrcInfo_0004bcd8)(param_1);
  return;
}


/* 0001eb28 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MprIf::Init(void)

{
  (*(code *)PTR_Init_0004bcdc)();
  return;
}


/* 0001eb34 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void * mmap(void *__addr,size_t __len,int __prot,int __flags,int __fd,__off_t __offset)

{
  void *pvVar1;
  
  pvVar1 = (void *)(*(code *)PTR_mmap_0004bce0)(__addr);
  return pvVar1;
}


/* 0001eb40 */

void __thiscall MprCtrlStillMgr::PrintStillData(MprCtrlStillMgr *this)

{
  (*(code *)PTR_PrintStillData_0004bce4)(this);
  return;
}


/* 0001eb4c */

void MprCtrl::GetMediaIdList(uint param_1,uint *param_2,uint *param_3)

{
  (*(code *)PTR_GetMediaIdList_0004bce8)(param_1);
  return;
}


/* 0001eb5c */

void DmmAccess::FreeDmmMemory(int param_1,uint param_2)

{
  (*(code *)PTR_FreeDmmMemory_0004bcec)(param_1);
  return;
}


/* 0001eb68 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MonCtrl::ConPutMessage(char *param_1)

{
  (*(code *)PTR_ConPutMessage_0004bcf0)(param_1);
  return;
}


/* 0001eb74 */

void MprCnv::Exchg_ImgDirectionRef(ImgDirectionRef *param_1,ImgDirectionRef *param_2)

{
  (*(code *)PTR_Exchg_ImgDirectionRef_0004bcf4)(param_1);
  return;
}


/* 0001eb80 */

void MprCnv::Exchg_AltitudeRef(AltitudeRef *param_1,AltitudeRef *param_2)

{
  (*(code *)PTR_Exchg_AltitudeRef_0004bcf8)(param_1);
  return;
}


/* 0001eb8c */

void __thiscall MprCtrl::_MediaInfo::SetMMgrId(void)

{
  (*(code *)PTR_SetMMgrId_0004bcfc)();
  return;
}


/* 0001eb98 */

void MprCtrl::CnvTvSystem(void)

{
  (*(code *)PTR_CnvTvSystem_0004bd00)();
  return;
}


/* 0001eba4 */

void MprCtrlLog::SetErrLog(uchar param_1,uint param_2,ushort param_3,char *param_4)

{
  (*(code *)PTR_SetErrLog_0004bd04)(param_1,param_2,param_3);
  return;
}


/* 0001ebb0 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MonCtrl::ConPrintf(char *param_1,...)

{
  (*(code *)PTR_ConPrintf_0004bd08)(param_1);
  return;
}


/* 0001ebbc */

void __thiscall MWF::EventHandler::EventHandler(EventHandler *this)

{
  (*(code *)PTR_EventHandler_0004bd0c)(this);
  return;
}


/* 0001ebc8 */

void __thiscall MprCtrl::_MprEnterInfo::Release(_MprEnterInfo *this,uint param_1)

{
  (*(code *)PTR_Release_0004bd10)(this);
  return;
}


/* 0001ebd4 */

void DmmAccessPLA::SetExtListPackOnPackHeader(void *param_1,void *param_2,uint param_3)

{
  (*(code *)PTR_SetExtListPackOnPackHeader_0004bd14)(param_1);
  return;
}


/* 0001ebe0 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::EventWrapper::SetSendId(uint param_1)

{
  (*(code *)PTR_SetSendId_0004bd18)(param_1);
  return;
}


/* 0001ebec */

void __thiscall MWF::EventSender::EventSender(EventSender *this)

{
  (*(code *)PTR_EventSender_0004bd1c)(this);
  return;
}


/* 0001ebf8 */

void MprCnv::Exchg_SpeedRef(SpeedRef *param_1,SpeedRef *param_2)

{
  (*(code *)PTR_Exchg_SpeedRef_0004bd20)(param_1);
  return;
}


/* 0001ec04 */

void __thiscall MprCtrlStillMgr::CreateStillData(MprCtrlStillMgr *this)

{
  (*(code *)PTR_CreateStillData_0004bd24)(this);
  return;
}


/* 0001ec10 */

void __thiscall MprCtrlUpmEvent::~MprCtrlUpmEvent(MprCtrlUpmEvent *this)

{
  (*(code *)PTR__MprCtrlUpmEvent_0004bd28)(this);
  return;
}


/* 0001ec1c */

void MprCtrl::PrintInfo(uint param_1)

{
  (*(code *)PTR_PrintInfo_0004bd2c)(param_1);
  return;
}


/* 0001ec28 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::EventWrapper::SendAndRecv(void *param_1,int param_2,void *param_3,int param_4)

{
  (*(code *)PTR_SendAndRecv_0004bd30)(param_1);
  return;
}


/* 0001ec34 */

void MprCnv::Exchg_GPSTimeStamp(GPSTimeStamp *param_1,GPSTimeStamp *param_2)

{
  (*(code *)PTR_Exchg_GPSTimeStamp_0004bd34)(param_1);
  return;
}


/* 0001ec40 */

void MprCtrlUpmEvent::CallbackPoint(void *param_1,int param_2,void *param_3,uint param_4)

{
  (*(code *)PTR_CallbackPoint_0004bd38)(param_1);
  return;
}


/* 0001ec4c */

void __thiscall MWF::ObjSignal::ObjSignal(ObjSignal *this)

{
  (*(code *)PTR_ObjSignal_0004bd3c)(this);
  return;
}


/* 0001ec58 */

void DmmAccess::PrintAllModeTable(void)

{
  (*(code *)PTR_PrintAllModeTable_0004bd40)();
  return;
}


/* 0001ec64 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MprIf::SetCreateParam_SerialNumber(ulong param_1)

{
  (*(code *)PTR_SetCreateParam_SerialNumber_0004bd44)(param_1);
  return;
}


/* 0001ec70 */

void __thiscall MprCtrl::_MediaInfo::RemoveMMgrId(_MediaInfo *this,uint param_1)

{
  (*(code *)PTR_RemoveMMgrId_0004bd48)(this);
  return;
}


/* 0001ec7c */

void __thiscall MWF::ObjLock::~ObjLock(ObjLock *this)

{
  (*(code *)PTR__ObjLock_0004bd4c)(this);
  return;
}


/* 0001ec88 */

void __thiscall MonCtrl::MonCtrl(MonCtrl *this,char *param_1,bool param_2)

{
  (*(code *)PTR_MonCtrl_0004bd50)(this,param_1,param_2);
  return;
}


/* 0001ec94 */

void __cxa_guard_acquire(void)

{
  (*(code *)PTR___cxa_guard_acquire_0004bd54)();
  return;
}


/* 0001eca0 */

void DmmAccess::FreeDmmExtList(t_unitTypeConvertList *param_1,uint param_2)

{
  (*(code *)PTR_FreeDmmExtList_0004bd58)(param_1);
  return;
}


/* 0001ecbc */

void DmmAccessPLA::SetExtListOnPack(void *param_1,uint param_2,uint param_3,uint param_4)

{
  (*(code *)PTR_SetExtListOnPack_0004bd60)(param_1);
  return;
}


/* 0001ecc8 */

void __thiscall MprCtrl::_MprEnterInfo::Init(_MprEnterInfo *this)

{
  (*(code *)PTR_Init_0004bd64)(this);
  return;
}


/* 0001ecd4 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::ObjMsg::AddParam(uint param_1,Param *param_2)

{
  (*(code *)PTR_AddParam_0004bd68)(param_1);
  return;
}


/* 0001ece0 */

void MprCtrlStillMgr::GetDualRecStillMode(void)

{
  (*(code *)PTR_GetDualRecStillMode_0004bd6c)();
  return;
}


/* 0001ed0c */

void __thiscall StatMgr::~StatMgr(StatMgr *this)

{
  (*(code *)PTR__StatMgr_0004bd78)(this);
  return;
}


/* 0001ed18 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void operator_delete(void *param_1)

{
  (*(code *)PTR_operator_delete_0004bd7c)(param_1);
  return;
}


/* 0001ed24 */

void MprCtrl::IsDpofSupport(void)

{
  (*(code *)PTR_IsDpofSupport_0004bd80)();
  return;
}


/* 0001ed30 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MprIf::SetCreateParam_RecCamInfoParam(bool param_1)

{
  (*(code *)PTR_SetCreateParam_RecCamInfoParam_0004bd84)(param_1);
  return;
}


/* 0001ed3c */

void MprCnv::Exchg_TrackRef(TrackRef *param_1,TrackRef *param_2)

{
  (*(code *)PTR_Exchg_TrackRef_0004bd88)(param_1);
  return;
}


/* 0001ed48 */

void MediaConfigWrapper::GetRsrcInhOffset(uint param_1,uint *param_2)

{
  (*(code *)PTR_GetRsrcInhOffset_0004bd8c)(param_1);
  return;
}


/* 0001ed64 */

void UtilStillSize::CalcScnOption(void)

{
  (*(code *)PTR_CalcScnOption_0004bd94)();
  return;
}


/* 0001ed70 */

void MprCnv::Exchg_SpeedRef(SpeedRef *param_1,SpeedRef *param_2)

{
  (*(code *)PTR_Exchg_SpeedRef_0004bd98)(param_1);
  return;
}


/* 0001ed7c */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MprIf::SetCreateParam_SupportMedia(ulong param_1)

{
  (*(code *)PTR_SetCreateParam_SupportMedia_0004bd9c)(param_1);
  return;
}


/* 0001ed88 */

void UtilStillSize::IsRecordingSCN(void)

{
  (*(code *)PTR_IsRecordingSCN_0004bda0)();
  return;
}


/* 0001ed94 */

void MprCnv::Exchg_LatitudeRef(LatitudeRef *param_1,LatitudeRef *param_2)

{
  (*(code *)PTR_Exchg_LatitudeRef_0004bda4)(param_1);
  return;
}


/* 0001eda0 */

void MprCtrl::IsDualRecOver18Mbps(void)

{
  (*(code *)PTR_IsDualRecOver18Mbps_0004bda8)();
  return;
}


/* 0001edac */

void MprCtrlMcmd::GetMonDbg(void)

{
  (*(code *)PTR_GetMonDbg_0004bdac)();
  return;
}


/* 0001edc8 */

void DmmAccess::PrintModeTable(int param_1)

{
  (*(code *)PTR_PrintModeTable_0004bdb4)(param_1);
  return;
}


/* 0001edd4 */

void __thiscall MprCtrlStillMgr::PrintStillBackup(MprCtrlStillMgr *this)

{
  (*(code *)PTR_PrintStillBackup_0004bdb8)(this);
  return;
}


/* 0001ede0 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::InhMgr::UpdateInhFactor(void)

{
  (*(code *)PTR_UpdateInhFactor_0004bdbc)();
  return;
}


/* 0001edec */

void MprCnv::Exchg_GpsStatus(GpsStatus *param_1,GpsStatus *param_2)

{
  (*(code *)PTR_Exchg_GpsStatus_0004bdc0)(param_1);
  return;
}


/* 0001edf8 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MonCtrl::ConPutDec(uint param_1)

{
  (*(code *)PTR_ConPutDec_0004bdc4)(param_1);
  return;
}


/* 0001ee04 */

void __thiscall StatMgr::CheckFunc(StatMgr *this,_FuncEntry *param_1,void *param_2,uint param_3)

{
  (*(code *)PTR_CheckFunc_0004bdc8)(this);
  return;
}


/* 0001ee10 */

void __thiscall MprCtrl::_MediaInfo::SetMediaId(_MediaInfo *this,uint param_1)

{
  (*(code *)PTR_SetMediaId_0004bdcc)(this);
  return;
}


/* 0001ee1c */

void __thiscall CapIdWrapper::Munmap(CapIdWrapper *this,int param_1,MemExtent *param_2)

{
  (*(code *)PTR_Munmap_0004bdd0)(this);
  return;
}


/* 0001ee28 */

void MprCtrl::DeleteMMgr(uint param_1)

{
  (*(code *)PTR_DeleteMMgr_0004bdd4)(param_1);
  return;
}


/* 0001ee34 */

void UtimeWrapper::TIME_CNV(OSAL_TIME *param_1,Time *param_2)

{
  (*(code *)PTR_TIME_CNV_0004bdd8)(param_1);
  return;
}


/* 0001ee40 */

void __thiscall
EventSwitcher::AddCallbackFunc
          (EventSwitcher *this,void *param_1,uint param_2,_CallbackEntry *param_3)

{
  (*(code *)PTR_AddCallbackFunc_0004bddc)(this);
  return;
}


/* 0001ee4c */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MprIf::DeleteMMgr(ulong param_1)

{
  (*(code *)PTR_DeleteMMgr_0004bde0)(param_1);
  return;
}


/* 0001ee5c */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void * memset(void *__s,int __c,size_t __n)

{
  void *pvVar1;
  
  pvVar1 = (void *)(*(code *)PTR_memset_0004bde4)(__s);
  return pvVar1;
}


/* 0001ee68 */

void MprCtrl::IsRelayRecSupport(void)

{
  (*(code *)PTR_IsRelayRecSupport_0004bde8)();
  return;
}


/* 0001ee74 */

void MprCnv::Exchg_LongitudeRef(LongitudeRef *param_1,LongitudeRef *param_2)

{
  (*(code *)PTR_Exchg_LongitudeRef_0004bdec)(param_1);
  return;
}


/* 0001ee80 */

void MprCtrlLog::SetUnitHandleLog(uchar param_1,ushort param_2,ushort param_3)

{
  (*(code *)PTR_SetUnitHandleLog_0004bdf0)(param_1,param_2,param_3);
  return;
}


/* 0001ee8c */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::ParamStd_Template<unsigned_char,(MWF::Param::Type)4>::GetValue(void)

{
  (*(code *)PTR_GetValue_0004bdf4)();
  return;
}


/* 0001ee98 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::ParamStd_Template<short,(MWF::Param::Type)5>::GetValue(void)

{
  (*(code *)PTR_GetValue_0004bdf8)();
  return;
}


/* 0001eeb4 */

void __thiscall MprCtrlUpmEvent::UpdateResourse(MprCtrlUpmEvent *this,uint param_1,bool param_2)

{
  (*(code *)PTR_UpdateResourse_0004be00)(this,param_1,param_2);
  return;
}


/* 0001eec0 */

void __cxa_end_cleanup(void)

{
  (*(code *)PTR___cxa_end_cleanup_0004be04)();
  return;
}


/* 0001eedc */

void MprCnv::Exchg_ExifSrcInfo(ExifSrcInfo *param_1,ExifSrcInfo *param_2)

{
  (*(code *)PTR_Exchg_ExifSrcInfo_0004be0c)(param_1);
  return;
}


/* 0001eee8 */

void DmmAccess::GetDmmExtList(t_unitTypeConvertList *param_1,ushort *param_2)

{
  (*(code *)PTR_GetDmmExtList_0004be10)(param_1);
  return;
}


/* 0001eef4 */

void MprObjectUtil::MwfInt8(ObjMsg *param_1,uint param_2)

{
  (*(code *)PTR_MwfInt8_0004be14)(param_1);
  return;
}


/* 0001ef00 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::EventWrapper::ClearCallBack(void)

{
  (*(code *)PTR_ClearCallBack_0004be18)();
  return;
}


/* 0001ef0c */

void UtimeWrapper::TIMEZONE_CNV(OSAL_TIMEZONE *param_1,Timezone *param_2)

{
  (*(code *)PTR_TIMEZONE_CNV_0004be1c)(param_1);
  return;
}


/* 0001ef18 */

void __thiscall MWF::ObjMsg::ObjMsg(void *this)

{
  (*(code *)PTR_ObjMsg_0004be20)(this);
  return;
}


/* 0001ef24 */

void MprCnv::Exchg_TrackRef(TrackRef *param_1,TrackRef *param_2)

{
  (*(code *)PTR_Exchg_TrackRef_0004be24)(param_1);
  return;
}


/* 0001ef30 */

void MonLib::ConPutStr(char *param_1)

{
  (*(code *)PTR_ConPutStr_0004be28)(param_1);
  return;
}


/* 0001ef3c */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::ObjPin::Connect(ObjPin *param_1,ObjStatusViewer *param_2)

{
  (*(code *)PTR_Connect_0004be2c)(param_1);
  return;
}


/* 0001ef58 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::ParamStd_Template<unsigned_int,(MWF::Param::Type)8>::GetValue(void)

{
  (*(code *)PTR_GetValue_0004be34)();
  return;
}


/* 0001ef64 */

void MprObjectUtil::MwfStruct(ObjMsg *param_1,uint param_2,uint param_3)

{
  (*(code *)PTR_MwfStruct_0004be38)(param_1);
  return;
}


/* 0001ef70 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::EventReceiver::RecvEvent(ObjMsg *param_1)

{
  (*(code *)PTR_RecvEvent_0004be3c)(param_1);
  return;
}


/* 0001ef7c */

void __thiscall MprCtrl::_MediaInfo::GetDsysId(_MediaInfo *this,uint param_1)

{
  (*(code *)PTR_GetDsysId_0004be40)(this);
  return;
}


/* 0001ef88 */

void __thiscall
MprCtrlStillMgr::GetStillDataInfo
          (MprCtrlStillMgr *this,int param_1,int param_2,int param_3,int param_4,int param_5,
          int param_6,StillDataInfo *param_7)

{
  (*(code *)PTR_GetStillDataInfo_0004be44)(this);
  return;
}


/* 0001ef94 */

void DmmAccess::DmmReuseAndOpen(uint param_1,ushort param_2)

{
  (*(code *)PTR_DmmReuseAndOpen_0004be48)(param_1,param_2);
  return;
}


/* 0001efa0 */

void BackupLib::GetEepData(uint param_1,uchar param_2,void *param_3)

{
  (*(code *)PTR_GetEepData_0004be4c)(param_1,param_2);
  return;
}


/* 0001efac */

void __thiscall
MprCtrlUpmEvent::GetCurPwrSpplyState(MprCtrlUpmEvent *this,int *param_1,int *param_2)

{
  (*(code *)PTR_GetCurPwrSpplyState_0004be50)(this);
  return;
}


/* 0001efb8 */

void __thiscall MprCtrlUpmEvent::RegenarateResourseAcsr(MprCtrlUpmEvent *this,uint param_1)

{
  (*(code *)PTR_RegenarateResourseAcsr_0004be54)(this);
  return;
}


/* 0001efc8 */

void DmmAccess::DmmAllocateNEWAndOpen_body
               (uint param_1,ushort param_2,ushort param_3,ushort param_4)

{
  (*(code *)PTR_DmmAllocateNEWAndOpen_body_0004be58)(param_1,param_2,param_3,param_4);
  return;
}


/* 0001efd4 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MprIf::SetAviManagedContentTypes(ulong param_1,ulong param_2)

{
  (*(code *)PTR_SetAviManagedContentTypes_0004be5c)(param_1);
  return;
}


/* 0001efe0 */

void __thiscall MprCtrl::_RecLineTable::_RecLineTable(_RecLineTable *this)

{
  (*(code *)PTR__RecLineTable_0004be60)(this);
  return;
}


/* 0001eff0 */

void DmmAccessPLA::GetUnitHandle(void *param_1)

{
  (*(code *)PTR_GetUnitHandle_0004be64)(param_1);
  return;
}


/* 0001effc */

void MprCtrlStillMgr::PrintStillSize(void)

{
  (*(code *)PTR_PrintStillSize_0004be68)();
  return;
}


/* 0001f008 */

void __thiscall EventSwitcher::SearchInstanceCell(EventSwitcher *this,void *param_1)

{
  (*(code *)PTR_SearchInstanceCell_0004be6c)(this);
  return;
}


/* 0001f014 */

void __thiscall
StateMgr::GetNextState(StateMgr *this,_FuncEntry *param_1,ObjMsg *param_2,int param_3)

{
  (*(code *)PTR_GetNextState_0004be70)(this);
  return;
}


/* 0001f020 */

void __thiscall MprCtrl::_RecLineTable::GetLine(_RecLineTable *this,uint param_1)

{
  (*(code *)PTR_GetLine_0004be74)(this);
  return;
}


/* 0001f02c */

void __thiscall MWF::RsrcAcsr::RsrcAcsr(void)

{
  (*(code *)PTR_RsrcAcsr_0004be78)();
  return;
}


/* 0001f038 */

void MprCtrl::DeleteDsys(uint param_1)

{
  (*(code *)PTR_DeleteDsys_0004be7c)(param_1);
  return;
}


/* 0001f044 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MonCtrl::ConPutStr(char *param_1)

{
  (*(code *)PTR_ConPutStr_0004be80)(param_1);
  return;
}


/* 0001f050 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::ParamStd_Template<int,(MWF::Param::Type)7>::GetValue(void)

{
  (*(code *)PTR_GetValue_0004be84)();
  return;
}


/* 0001f060 */

void MprCnv::Exchg_DegMinSec(DegMinSec *param_1,DegMinSec *param_2)

{
  (*(code *)PTR_Exchg_DegMinSec_0004be88)(param_1);
  return;
}


/* 0001f06c */

void StrUtil::StrrChr(char *param_1,uint param_2)

{
  (*(code *)PTR_StrrChr_0004be8c)(param_1);
  return;
}


/* 0001f07c */

void __thiscall UtimeWrapper::USleep(UtimeWrapper *this,ulonglong param_1)

{
  undefined4 in_r1;
  
  (*(code *)PTR_USleep_0004be90)(this,in_r1,(int)param_1,(int)(param_1 >> 0x20));
  return;
}


/* 0001f088 */

void __thiscall EventSwitcher::~EventSwitcher(EventSwitcher *this)

{
  (*(code *)PTR__EventSwitcher_0004be94)(this);
  return;
}


/* 0001f094 */

void DmmAccess::IsRemainMemory(t_unitTypeConvertList *param_1)

{
  (*(code *)PTR_IsRemainMemory_0004be98)(param_1);
  return;
}


/* 0001f0a4 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void free(void *__ptr)

{
  (*(code *)PTR_free_0004be9c)(__ptr);
  return;
}


/* 0001f0b0 */

void MprCtrl::GetAviManagedContentTypes(void)

{
  (*(code *)PTR_GetAviManagedContentTypes_0004bea0)();
  return;
}


/* 0001f0bc */

void __thiscall EventSwitcher::EventSwitcher(EventSwitcher *this)

{
  (*(code *)PTR_EventSwitcher_0004bea4)(this);
  return;
}


/* 0001f0c8 */

void MprCnv::Exchg_LatitudeRef(LatitudeRef *param_1,LatitudeRef *param_2)

{
  (*(code *)PTR_Exchg_LatitudeRef_0004bea8)(param_1);
  return;
}


/* 0001f0d4 */

void Log::Set(void)

{
  (*(code *)PTR_Set_0004beac)();
  return;
}


/* 0001f0e4 */

void MprCnv::Exchg_RationalValue(RationalValue *param_1,RationalValue *param_2)

{
  (*(code *)PTR_Exchg_RationalValue_0004beb0)(param_1);
  return;
}


/* 0001f0f0 */

void MprCnv::Exchg_HighlightRssTheme(HighlightTheme *param_1,HighlightRssTheme *param_2)

{
  (*(code *)PTR_Exchg_HighlightRssTheme_0004beb4)(param_1);
  return;
}


/* 0001f0fc */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MonCtrl::ConPutCRLF(void)

{
  (*(code *)PTR_ConPutCRLF_0004beb8)();
  return;
}


/* 0001f108 */

void UpmWrapper::POWER_TYPE_CNV(int param_1,PowerType *param_2)

{
  (*(code *)PTR_POWER_TYPE_CNV_0004bebc)(param_1);
  return;
}


/* 0001f114 */

void __thiscall MprCtrlUpmEvent::rsrcInfo::ChangeStat(void)

{
  (*(code *)PTR_ChangeStat_0004bec0)();
  return;
}


/* 0001f120 */

void MediaConfigWrapper::GetDeviceType(uint param_1)

{
  (*(code *)PTR_GetDeviceType_0004bec4)(param_1);
  return;
}


/* 0001f12c */

void MprCnv::Exchg_HighlightRssTheme(HighlightRssTheme *param_1,HighlightTheme *param_2)

{
  (*(code *)PTR_Exchg_HighlightRssTheme_0004bec8)(param_1);
  return;
}


/* 0001f138 */

void __thiscall EventSwitcher::AddInstance(EventSwitcher *this,void *param_1)

{
  (*(code *)PTR_AddInstance_0004becc)(this);
  return;
}


/* 0001f154 */

void UpmWrapper::BATTERY_CHECK_CNV(int param_1,BatteryCheck *param_2)

{
  (*(code *)PTR_BATTERY_CHECK_CNV_0004bed4)(param_1);
  return;
}


/* 0001f160 */

void MprCtrl::CreatePrefix(char *param_1,char *param_2)

{
  (*(code *)PTR_CreatePrefix_0004bed8)(param_1);
  return;
}


/* 0001f16c */

void __thiscall MprCtrlUpmEvent::UnregisterBusPowerEvent(MprCtrlUpmEvent *this)

{
  (*(code *)PTR_UnregisterBusPowerEvent_0004bedc)(this);
  return;
}


/* 0001f178 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void StrUtil::StrICmp(char *param_1,char *param_2)

{
  (*(code *)PTR_StrICmp_0004bee0)(param_1);
  return;
}


/* 0001f184 */

void __thiscall MprCtrl::_RecLineTable::Init(_RecLineTable *this)

{
  (*(code *)PTR_Init_0004bee4)(this);
  return;
}


/* 0001f190 */

void MprCtrl::IsMultiRecSupport(void)

{
  (*(code *)PTR_IsMultiRecSupport_0004bee8)();
  return;
}


/* 0001f19c */

void MprObjectUtil::MwfObjMsg(ObjMsg *param_1,uint param_2)

{
  (*(code *)PTR_MwfObjMsg_0004beec)(param_1);
  return;
}


/* 0001f1a8 */

void MprCtrlCnv::Init(void)

{
  (*(code *)PTR_Init_0004bef0)();
  return;
}


/* 0001f1b4 */

void osal_rcv_msg_tmo(void)

{
  (*(code *)PTR_osal_rcv_msg_tmo_0004bef4)();
  return;
}


/* 0001f1c0 */

void MprCtrl::GetModelName(char *param_1)

{
  (*(code *)PTR_GetModelName_0004bef8)(param_1);
  return;
}


/* 0001f1cc */

void __thiscall
UpmWrapper::RegisterCallBackForHeatAlert
          (UpmWrapper *this,uint param_1,_func_void_void_ptr_int_void_ptr_uint *param_2,
          void *param_3)

{
  (*(code *)PTR_RegisterCallBackForHeatAlert_0004befc)(this);
  return;
}


/* 0001f1d8 */

void osal_reg_msg_queue_cb(void)

{
  (*(code *)PTR_osal_reg_msg_queue_cb_0004bf00)();
  return;
}


/* 0001f1f4 */

void UtilStillSize::CnvStillSize(int param_1)

{
  (*(code *)PTR_CnvStillSize_0004bf08)(param_1);
  return;
}


/* 0001f200 */

void __thiscall MWF::InhMgr::InhMgr(InhMgr *this)

{
  (*(code *)PTR_InhMgr_0004bf0c)(this);
  return;
}


/* 0001f20c */

void MprCtrlLog::SetMemoryMapLog(uint param_1)

{
  (*(code *)PTR_SetMemoryMapLog_0004bf10)(param_1);
  return;
}


/* 0001f218 */

void DmmAccess::GetUnitHandle(void *param_1)

{
  (*(code *)PTR_GetUnitHandle_0004bf14)(param_1);
  return;
}


/* 0001f224 */

void __cxa_guard_release(void)

{
  (*(code *)PTR___cxa_guard_release_0004bf18)();
  return;
}


/* 0001f234 */

void MprCtrlLog::SetBasicLog(uchar param_1,ushort param_2,ushort param_3)

{
  (*(code *)PTR_SetBasicLog_0004bf1c)(param_1,param_2,param_3);
  return;
}


/* 0001f240 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MprIf::SetCallbackFunc
               (ulong param_1,_func_void_ulong_ulong_void_ptr_ulong_void_ptr *param_2,ulong param_3,
               void *param_4)

{
  (*(code *)PTR_SetCallbackFunc_0004bf20)(param_1);
  return;
}


/* 0001f24c */

void __thiscall StateMgr::~StateMgr(StateMgr *this)

{
  (*(code *)PTR__StateMgr_0004bf24)(this);
  return;
}


/* 0001f258 */

void MprCtrl::IsDvMode(void)

{
  (*(code *)PTR_IsDvMode_0004bf28)();
  return;
}


/* 0001f274 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MprIf::SetCreateParam_GpsParam(bool param_1)

{
  (*(code *)PTR_SetCreateParam_GpsParam_0004bf30)(param_1);
  return;
}


/* 0001f284 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

size_t strlen(char *__s)

{
  size_t sVar1;
  
  sVar1 = (*(code *)PTR_strlen_0004bf34)(__s);
  return sVar1;
}


/* 0001f290 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::EventReceiver::GenerateEventId(uint param_1)

{
  (*(code *)PTR_GenerateEventId_0004bf38)(param_1);
  return;
}


/* 0001f29c */

void MprCtrlLog::SetParamLog
               (uchar param_1,ushort param_2,ushort param_3,ushort param_4,ushort param_5)

{
  (*(code *)PTR_SetParamLog_0004bf3c)(param_1,param_2,param_3,param_4);
  return;
}


/* 0001f2a8 */

void DmmAccess::UnitTypeTableSelect(int param_1)

{
  (*(code *)PTR_UnitTypeTableSelect_0004bf40)(param_1);
  return;
}


/* 0001f2b4 */

void __thiscall MWF::ObjLock::ObjLock(ObjLock *this)

{
  (*(code *)PTR_ObjLock_0004bf44)(this);
  return;
}


/* 0001f2c0 */

void __thiscall
UpmWrapper::RegisterCallBackForPowerStatus
          (UpmWrapper *this,uint param_1,_func_void_void_ptr_int_void_ptr_uint *param_2,
          void *param_3)

{
  (*(code *)PTR_RegisterCallBackForPowerStatus_0004bf48)(this);
  return;
}


/* 0001f2dc */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::ParamStd_Template<unsigned_int,(MWF::Param::Type)8>::ParamStd_Template(uint param_1)

{
  (*(code *)PTR_ParamStd_Template_0004bf50)(param_1);
  return;
}


/* 0001f2e8 */

void MprCnv::Exchg_ImgDirectionRef(ImgDirectionRef *param_1,ImgDirectionRef *param_2)

{
  (*(code *)PTR_Exchg_ImgDirectionRef_0004bf54)(param_1);
  return;
}


/* 0001f2f4 */

void osal_valloc_msg_wait(void)

{
  (*(code *)PTR_osal_valloc_msg_wait_0004bf58)();
  return;
}


/* 0001f304 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void * memcpy(void *__dest,void *__src,size_t __n)

{
  void *pvVar1;
  
  pvVar1 = (void *)(*(code *)PTR_memcpy_0004bf5c)(__dest);
  return pvVar1;
}


/* 0001f310 */

void __thiscall MprObjectUtil::MwfException::MwfException(void)

{
  (*(code *)PTR_MwfException_0004bf60)();
  return;
}


/* 0001f31c */

void DmmAccessPLA::SetExtListPackStatus
               (void *param_1,uint param_2,ushort param_3,ushort param_4,uint param_5)

{
  (*(code *)PTR_SetExtListPackStatus_0004bf64)(param_1,param_2,param_3,param_4);
  return;
}


/* 0001f328 */

void MWF::ObjMsg::GetParam(void)

{
  (*(code *)PTR_GetParam_0004bf68)();
  return;
}


/* 0001f334 */

void __thiscall MprCtrl::_MediaInfo::SetDsysId(void)

{
  (*(code *)PTR_SetDsysId_0004bf6c)();
  return;
}


/* 0001f340 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MprIf::NewHddAviMMgr(HddAviCreateParam *param_1,ulong *param_2)

{
  (*(code *)PTR_NewHddAviMMgr_0004bf70)(param_1);
  return;
}


/* 0001f34c */

void MprCnv::Exchg_GpsMeasureMode(GpsMeasureMode *param_1,GpsMeasureMode *param_2)

{
  (*(code *)PTR_Exchg_GpsMeasureMode_0004bf74)(param_1);
  return;
}


/* 0001f35c */

void MemUtil::MemSet8(void *param_1,uchar param_2,int param_3)

{
  (*(code *)PTR_MemSet8_0004bf78)(param_1,param_2);
  return;
}


/* 0001f368 */

void osal_unreg_msg_queue_cb(void)

{
  (*(code *)PTR_osal_unreg_msg_queue_cb_0004bf7c)();
  return;
}


/* 0001f374 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::Struct::GetSize(void)

{
  (*(code *)PTR_GetSize_0004bf80)();
  return;
}


/* 0001f380 */

void __thiscall EventHandlerWrapper::EventHandlerWrapper(EventHandlerWrapper *this)

{
  (*(code *)PTR_EventHandlerWrapper_0004bf84)(this);
  return;
}


/* 0001f38c */

void MprCnv::Exchg_LocalTime(T_LTM *param_1,LocalTime *param_2)

{
  (*(code *)PTR_Exchg_LocalTime_0004bf88)(param_1);
  return;
}


/* 0001f398 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MonLib::MonFlgDel(char *param_1)

{
  (*(code *)PTR_MonFlgDel_0004bf8c)(param_1);
  return;
}


/* 0001f3b4 */

void DmmAccess::DmmAllocateAndOpen(uint param_1)

{
  (*(code *)PTR_DmmAllocateAndOpen_0004bf94)(param_1);
  return;
}


/* 0001f3c0 */

void MprCtrlCnv::Exchg_DeviceType(DeviceType *param_1,DeviceType *param_2)

{
  (*(code *)PTR_Exchg_DeviceType_0004bf98)(param_1);
  return;
}


/* 0001f3cc */

void __cxa_call_unexpected(void)

{
  (*(code *)PTR___cxa_call_unexpected_0004bf9c)();
  return;
}


/* 0001f3d8 */

void MprCtrl::CreateMMgr(uint param_1)

{
  (*(code *)PTR_CreateMMgr_0004bfa0)(param_1);
  return;
}


/* 0001f3e4 */

void __thiscall MprCtrl::_MprEnterInfo::Get(_MprEnterInfo *this,uint param_1)

{
  (*(code *)PTR_Get_0004bfa4)(this);
  return;
}


/* 0001f3f0 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::ObjSignal::ClearSignal(void)

{
  (*(code *)PTR_ClearSignal_0004bfa8)();
  return;
}


/* 0001f3fc */

void __thiscall MprCtrl::_MprEnterInfo::_MprEnterInfo(_MprEnterInfo *this)

{
  (*(code *)PTR__MprEnterInfo_0004bfac)(this);
  return;
}


/* 0001f408 */

void __thiscall MprCtrlStillMgr::MprCtrlStillMgr(MprCtrlStillMgr *this)

{
  (*(code *)PTR_MprCtrlStillMgr_0004bfb0)(this);
  return;
}


/* 0001f414 */

void __thiscall MprCtrlStillMgr::~MprCtrlStillMgr(MprCtrlStillMgr *this)

{
  (*(code *)PTR__MprCtrlStillMgr_0004bfb4)(this);
  return;
}


/* 0001f420 */

void MprObjectUtil::MwfUInt16(ObjMsg *param_1,uint param_2)

{
  (*(code *)PTR_MwfUInt16_0004bfb8)(param_1);
  return;
}


/* 0001f42c */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::EventWrapper::RegisterCallBack
               (uint param_1,_func_void_void_ptr_int_void_ptr_uint *param_2,void *param_3)

{
  (*(code *)PTR_RegisterCallBack_0004bfbc)(param_1);
  return;
}


/* 0001f438 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MonCtrl::ConPutStr(char *param_1,uint param_2)

{
  (*(code *)PTR_ConPutStr_0004bfc0)(param_1);
  return;
}


/* 0001f454 */

void MediaConfigWrapper::ERR_CNV(int param_1)

{
  (*(code *)PTR_ERR_CNV_0004bfc8)(param_1);
  return;
}


/* 0001f460 */

void osal_snd_msg(void)

{
  (*(code *)PTR_osal_snd_msg_0004bfcc)();
  return;
}


/* 0001f46c */

void StrUtil::StrLen(char *param_1)

{
  (*(code *)PTR_StrLen_0004bfd0)(param_1);
  return;
}


/* 0001f478 */

void __thiscall MprCtrl::_MediaInfo::Init(_MediaInfo *this)

{
  (*(code *)PTR_Init_0004bfd4)(this);
  return;
}


/* 0001f484 */

void MprObjectUtil::MwfUInt64(ObjMsg *param_1,uint param_2)

{
  (*(code *)PTR_MwfUInt64_0004bfd8)(param_1);
  return;
}


/* 0001f4a4 */

void MprCnv::Exchg_AreaInfo(AreaInfo *param_1,AreaInfo *param_2)

{
  (*(code *)PTR_Exchg_AreaInfo_0004bfe0)(param_1);
  return;
}


/* 0001f4b0 */

void StrUtil::StrCmp(char *param_1,char *param_2)

{
  (*(code *)PTR_StrCmp_0004bfe4)(param_1);
  return;
}


/* 0001f4bc */

void __aeabi_uidiv(void)

{
  (*(code *)PTR___aeabi_uidiv_0004bfe8)();
  return;
}


/* 0001f4c8 */

void MprCtrl::GetSupportContentTypes(void)

{
  (*(code *)PTR_GetSupportContentTypes_0004bfec)();
  return;
}


/* 0001f4d4 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MonCtrl::ConPutStrAndCRLF(char *param_1)

{
  (*(code *)PTR_ConPutStrAndCRLF_0004bff0)(param_1);
  return;
}


/* 0001f4e0 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::ParamStd_Template<signed_char,(MWF::Param::Type)3>::GetValue(void)

{
  (*(code *)PTR_GetValue_0004bff4)();
  return;
}


/* 0001f4fc */

void EventHandlerWrapper::WaitEvent(uint param_1)

{
  (*(code *)PTR_WaitEvent_0004bffc)(param_1);
  return;
}


/* 0001f508 */

void MprCtrlLog::SetStartApiLog(uchar param_1,ushort param_2)

{
  (*(code *)PTR_SetStartApiLog_0004c000)(param_1,param_2);
  return;
}


/* 0001f514 */

void MprCtrlCnv::Exchg_StillAspect(SAspect *param_1,ContentAspect *param_2)

{
  (*(code *)PTR_Exchg_StillAspect_0004c004)(param_1);
  return;
}


/* 0001f520 */

void StrUtil::StrCat(char *param_1,char *param_2)

{
  (*(code *)PTR_StrCat_0004c008)(param_1);
  return;
}


/* 0001f52c */

void StrUtil::StrNCpy(char *param_1,char *param_2,int param_3)

{
  (*(code *)PTR_StrNCpy_0004c00c)(param_1);
  return;
}


/* 0001f538 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MprIf::GetPreFirstMountInfo(PreFirstMountInfo *param_1,ulong param_2)

{
  (*(code *)PTR_GetPreFirstMountInfo_0004c010)(param_1);
  return;
}


/* 0001f544 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::RsrcAcsr::Release(void)

{
  (*(code *)PTR_Release_0004c014)();
  return;
}


/* 0001f550 */

void __thiscall MprCtrlInputEvent::~MprCtrlInputEvent(MprCtrlInputEvent *this)

{
  (*(code *)PTR__MprCtrlInputEvent_0004c018)(this);
  return;
}


/* 0001f56c */

void MprObjectUtil::MwfInt32(ObjMsg *param_1,uint param_2)

{
  (*(code *)PTR_MwfInt32_0004c020)(param_1);
  return;
}


/* 0001f578 */

void __thiscall MprCtrlStillMgr::GetStillDataTable(MprCtrlStillMgr *this)

{
  (*(code *)PTR_GetStillDataTable_0004c024)(this);
  return;
}


/* 0001f584 */

void MprObjectUtil::MwfBool(ObjMsg *param_1,uint param_2)

{
  (*(code *)PTR_MwfBool_0004c028)(param_1);
  return;
}


/* 0001f590 */

void __thiscall MprCtrl::_MediaInfo::_MediaInfo(_MediaInfo *this)

{
  (*(code *)PTR__MediaInfo_0004c02c)(this);
  return;
}


/* 0001f59c */

void UtimeWrapper::ERR_CNV(void)

{
  (*(code *)PTR_ERR_CNV_0004c030)();
  return;
}


/* 0001f5ac */

void MprCnv::Exchg_RationalValue(RationalValue *param_1,RationalValue *param_2)

{
  (*(code *)PTR_Exchg_RationalValue_0004c034)(param_1);
  return;
}


/* 0001f5b8 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void * operator_new(uint param_1)

{
  void *pvVar1;
  
  pvVar1 = (void *)(*(code *)PTR_operator_new_0004c038)(param_1);
  return pvVar1;
}


/* 0001f5c4 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MprIf::SetCreateParam_StillSizeInfo(StillSizeInfo *param_1,ulong param_2)

{
  (*(code *)PTR_SetCreateParam_StillSizeInfo_0004c03c)(param_1);
  return;
}


/* 0001f5d0 */

void MWF::InhMgr::ChangeInhFactorStatus(void)

{
  (*(code *)PTR_ChangeInhFactorStatus_0004c040)();
  return;
}


/* 0001f5dc */

void MprCtrl::GetStillRecInfo(StillSizeInfo *param_1,int *param_2,int *param_3,uint *param_4)

{
  (*(code *)PTR_GetStillRecInfo_0004c044)(param_1);
  return;
}


/* 0001f5e8 */

void MprIf::SetCreateParam_dualRecStillInfo(void)

{
  (*(code *)PTR_SetCreateParam_dualRecStillInfo_0004c048)();
  return;
}


/* 0001f5f4 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

char * strstr(char *__haystack,char *__needle)

{
  char *pcVar1;
  
  pcVar1 = (char *)(*(code *)PTR_strstr_0004c04c)(__haystack);
  return pcVar1;
}


/* 0001f600 */

void MprCtrl::GetSerialNumber(void)

{
  (*(code *)PTR_GetSerialNumber_0004c050)();
  return;
}


/* 0001f60c */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int close(int __fd)

{
  int iVar1;
  
  iVar1 = (*(code *)PTR_close_0004c054)(__fd);
  return iVar1;
}


/* 0001f618 */

void MprCtrl::PrintVersion(void)

{
  (*(code *)PTR_PrintVersion_0004c058)();
  return;
}


/* 0001f624 */

void UpmWrapper::GetAcBatteryCheckInfo(void)

{
  (*(code *)PTR_GetAcBatteryCheckInfo_0004c05c)();
  return;
}


/* 0001f630 */

void MprCnv::Exchg_AltitudeRef(AltitudeRef *param_1,AltitudeRef *param_2)

{
  (*(code *)PTR_Exchg_AltitudeRef_0004c060)(param_1);
  return;
}


/* 0001f63c */

void MprCtrlMcmd::UnregisterCommand(void)

{
  (*(code *)PTR_UnregisterCommand_0004c064)();
  return;
}


/* 0001f648 */

void MediaConfigWrapper::DEVICE_TYPE_CNV(uint param_1)

{
  (*(code *)PTR_DEVICE_TYPE_CNV_0004c068)(param_1);
  return;
}


/* 0001f654 */

void MprCtrl::IsGpsSupport(void)

{
  (*(code *)PTR_IsGpsSupport_0004c06c)();
  return;
}


/* 0001f660 */

void UtilStillSize::CnvDualRecSize(int param_1)

{
  (*(code *)PTR_CnvDualRecSize_0004c070)(param_1);
  return;
}


/* 0001f66c */

void __thiscall MprCtrlInputEvent::Clear(MprCtrlInputEvent *this,uint param_1)

{
  (*(code *)PTR_Clear_0004c074)(this);
  return;
}


/* 0001f688 */

void MprCnv::Exchg_GPSTimeStamp(GPSTimeStamp *param_1,GPSTimeStamp *param_2)

{
  (*(code *)PTR_Exchg_GPSTimeStamp_0004c07c)(param_1);
  return;
}


/* 0001f694 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void * operator_new__(uint param_1)

{
  void *pvVar1;
  
  pvVar1 = (void *)(*(code *)PTR_operator_new___0004c080)(param_1);
  return pvVar1;
}


/* 0001f6a0 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MprIf::Destroy(MprIf *param_1)

{
  (*(code *)PTR_Destroy_0004c084)(param_1);
  return;
}


/* 0001f6ac */

void UtilList::GetTopCellFromList(_utlList *param_1)

{
  (*(code *)PTR_GetTopCellFromList_0004c088)(param_1);
  return;
}


/* 0001f6b8 */

void __thiscall
MWF::ParamStd_Template<unsigned_int,(MWF::Param::Type)8>::~ParamStd_Template
          (ParamStd_Template<unsigned_int,(MWF::Param::Type)8> *this)

{
  (*(code *)PTR__ParamStd_Template_0004c08c)(this);
  return;
}


/* 0001f6c4 */

void __aeabi_uidivmod(void)

{
  (*(code *)PTR___aeabi_uidivmod_0004c090)();
  return;
}


/* 0001f6d0 */

void MWF::RsrcAcsr::Acquire(void)

{
  (*(code *)PTR_Acquire_0004c094)();
  return;
}


/* 0001f6ec */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void StrUtil::StrDecToUInt32(char *param_1)

{
  (*(code *)PTR_StrDecToUInt32_0004c09c)(param_1);
  return;
}


/* 0001f6f8 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::EventIdFactory::ReleaseId(uint param_1)

{
  (*(code *)PTR_ReleaseId_0004c0a0)(param_1);
  return;
}


/* 0001f704 */

void MprCtrl::GetDualRecType(void)

{
  (*(code *)PTR_GetDualRecType_0004c0a4)();
  return;
}


/* 0001f710 */

void __thiscall
MprCtrlStillMgr::CalcStillData_JPG
          (MprCtrlStillMgr *this,int param_1,int param_2,int param_3,int param_4,uint param_5,
          uint *param_6,uint *param_7)

{
  (*(code *)PTR_CalcStillData_JPG_0004c0a8)(this);
  return;
}


/* 0001f71c */

void __thiscall MWF::EventWrapper::~EventWrapper(EventWrapper *this)

{
  (*(code *)PTR__EventWrapper_0004c0ac)(this);
  return;
}


/* 0001f728 */

void __thiscall ConnectPinWrapper::~ConnectPinWrapper(ConnectPinWrapper *this)

{
  (*(code *)PTR__ConnectPinWrapper_0004c0b0)(this);
  return;
}


/* 0001f734 */

void __thiscall
MprCtrlStillMgr::CalcStillData_SMV
          (MprCtrlStillMgr *this,int param_1,int param_2,int param_3,int param_4,uint param_5,
          uint *param_6,uint *param_7)

{
  (*(code *)PTR_CalcStillData_SMV_0004c0b4)(this);
  return;
}


/* 0001f740 */

void DmmAccess::GetOSALRetMsg(void)

{
  (*(code *)PTR_GetOSALRetMsg_0004c0b8)();
  return;
}


/* 0001f74c */

void __thiscall UpmWrapper::UpmWrapper(UpmWrapper *this)

{
  (*(code *)PTR_UpmWrapper_0004c0bc)(this);
  return;
}


/* 0001f758 */

void __thiscall UpmWrapper::ClearCallBackForBatteryLevel(UpmWrapper *this)

{
  (*(code *)PTR_ClearCallBackForBatteryLevel_0004c0c0)(this);
  return;
}


/* 0001f764 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void * malloc(size_t __size)

{
  void *pvVar1;
  
  pvVar1 = (void *)(*(code *)PTR_malloc_0004c0c4)(__size);
  return pvVar1;
}


/* 0001f770 */

void DmmAccess::FreeDmmMemory(int param_1)

{
  (*(code *)PTR_FreeDmmMemory_0004c0c8)(param_1);
  return;
}


/* 0001f77c */

void MprCtrl::GetTvSystem(void)

{
  (*(code *)PTR_GetTvSystem_0004c0cc)();
  return;
}


/* 0001f788 */

void MprObjectUtil::MwfUInt8(ObjMsg *param_1,uint param_2)

{
  (*(code *)PTR_MwfUInt8_0004c0d0)(param_1);
  return;
}


/* 0001f794 */

void __thiscall MonCtrl::~MonCtrl(MonCtrl *this)

{
  (*(code *)PTR__MonCtrl_0004c0d4)(this);
  return;
}


/* 0001f7a4 */

void UpmWrapper::ERR_CNV(void)

{
  (*(code *)PTR_ERR_CNV_0004c0d8)();
  return;
}


/* 0001f7b0 */

void DmmAccess::CheckOSALRetCode(void)

{
  (*(code *)PTR_CheckOSALRetCode_0004c0dc)();
  return;
}


/* 0001f7bc */

void DmmAccess::CheckDMMRetCode(short param_1,char *param_2)

{
  (*(code *)PTR_CheckDMMRetCode_0004c0e0)((int)param_1);
  return;
}


/* 0001f7c8 */

void __thiscall MWF::ObjMsg::ObjMsg(void *this,uint param_1,uint param_2)

{
  (*(code *)PTR_ObjMsg_0004c0e4)(this);
  return;
}


/* 0001f7d4 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MonCtrl::ConPutDec(uint param_1,uint param_2)

{
  (*(code *)PTR_ConPutDec_0004c0e8)(param_1);
  return;
}


/* 0001f7e0 */

void MprCtrl::SetModelVersion(void)

{
  (*(code *)PTR_SetModelVersion_0004c0ec)();
  return;
}


/* 0001f7ec */

void __thiscall MWF::ObjSignal::~ObjSignal(ObjSignal *this)

{
  (*(code *)PTR__ObjSignal_0004c0f0)(this);
  return;
}


/* 0001f7f8 */

void __cxa_allocate_exception(void)

{
  (*(code *)PTR___cxa_allocate_exception_0004c0f4)();
  return;
}


/* 0001f804 */

void MprCtrl::IsStillCacheSupport(void)

{
  (*(code *)PTR_IsStillCacheSupport_0004c0f8)();
  return;
}


/* 0001f810 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::Struct::GetValue(void)

{
  (*(code *)PTR_GetValue_0004c0fc)();
  return;
}


/* 0001f81c */

void BackupLib::GetDataSize(uint param_1)

{
  (*(code *)PTR_GetDataSize_0004c100)(param_1);
  return;
}


/* 0001f82c */

void MprCtrlMcmd::RegisterCommand(void)

{
  (*(code *)PTR_RegisterCommand_0004c104)();
  return;
}


/* 0001f838 */

void UtilStillSize::CnvStillAspect(int param_1)

{
  (*(code *)PTR_CnvStillAspect_0004c108)(param_1);
  return;
}


/* 0001f844 */

void DmmAccess::CnvAreaId2ModeSubArea(uint param_1)

{
  (*(code *)PTR_CnvAreaId2ModeSubArea_0004c10c)(param_1);
  return;
}


/* 0001f850 */

void __thiscall MprCtrl::_MediaInfo::GetMMgrId(_MediaInfo *this,uint param_1)

{
  (*(code *)PTR_GetMMgrId_0004c110)(this);
  return;
}


/* 0001f860 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MonCtrl::ConPrintfMessage(char *param_1,...)

{
  (*(code *)PTR_ConPrintfMessage_0004c114)(param_1);
  return;
}


/* 0001f86c */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::ObjMsg::GetCategoryId(void)

{
  (*(code *)PTR_GetCategoryId_0004c118)();
  return;
}


/* 0001f878 */

void __thiscall MprCtrlUpmEvent::MprCtrlUpmEvent(MprCtrlUpmEvent *this)

{
  (*(code *)PTR_MprCtrlUpmEvent_0004c11c)(this);
  return;
}


/* 0001f884 */

void MprCnv::Exchg_GpsStatus(GpsStatus *param_1,GpsStatus *param_2)

{
  (*(code *)PTR_Exchg_GpsStatus_0004c120)(param_1);
  return;
}


/* 0001f890 */

void __aeabi_uldivmod(void)

{
  (*(code *)PTR___aeabi_uldivmod_0004c124)();
  return;
}


/* 0001f89c */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MprIf::SetCreateParam_SupportContentTypes(ulong param_1)

{
  (*(code *)PTR_SetCreateParam_SupportContentTypes_0004c128)(param_1);
  return;
}


/* 0001f8a8 */

void __thiscall UpmWrapper::ClearCallBackForPowerStatus(UpmWrapper *this)

{
  (*(code *)PTR_ClearCallBackForPowerStatus_0004c12c)(this);
  return;
}


/* 0001f8b4 */

void __thiscall
MprCtrlStillMgr::CalcStillData_RAW
          (MprCtrlStillMgr *this,int param_1,int param_2,int param_3,uint *param_4,uint *param_5)

{
  (*(code *)PTR_CalcStillData_RAW_0004c130)(this);
  return;
}


/* 0001f8c4 */

void __thiscall MWF::ObjLock::Unlock(ObjLock *this)

{
  (*(code *)PTR_Unlock_0004c134)(this);
  return;
}


/* 0001f8d0 */

void __thiscall StatMgr::CallFunc(StatMgr *this,_FuncEntry *param_1,void *param_2,uint param_3)

{
  (*(code *)PTR_CallFunc_0004c138)(this);
  return;
}


/* 0001f8e0 */

void __thiscall MprCtrlStillMgr::GetStillSizeTable(MprCtrlStillMgr *this)

{
  (*(code *)PTR_GetStillSizeTable_0004c13c)(this);
  return;
}


/* 0001f8ec */

void __thiscall MprCtrlStillMgr::Calc_Align(MprCtrlStillMgr *this,int param_1)

{
  (*(code *)PTR_Calc_Align_0004c140)(this);
  return;
}


/* 0001f8f8 */

void UpmWrapper::GetTemperatureRange(void)

{
  (*(code *)PTR_GetTemperatureRange_0004c144)();
  return;
}


/* 0001f904 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MprIf::SetCallbackFunc
               (_func_void_ulong_ulong_void_ptr_ulong_void_ptr *param_1,ulong param_2,void *param_3)

{
  (*(code *)PTR_SetCallbackFunc_0004c148)(param_1);
  return;
}


/* 0001f910 */

void UpmWrapper::TEMPERATURE_CNV(int param_1,TemperatureRange *param_2)

{
  (*(code *)PTR_TEMPERATURE_CNV_0004c14c)(param_1);
  return;
}


/* 0001f91c */

void MprObjectUtil::MwfInt16(ObjMsg *param_1,uint param_2)

{
  (*(code *)PTR_MwfInt16_0004c150)(param_1);
  return;
}


/* 0001f928 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::EventReceiver::SetEventHandler(EventHandler *param_1)

{
  (*(code *)PTR_SetEventHandler_0004c154)(param_1);
  return;
}


/* 0001f934 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::ObjPin::Disconnect(void)

{
  (*(code *)PTR_Disconnect_0004c158)();
  return;
}


/* 0001f940 */

void __thiscall MprCtrl::_RecLineTable::Remove(_RecLineTable *this,uint param_1)

{
  (*(code *)PTR_Remove_0004c15c)(this);
  return;
}


/* 0001f94c */

void MprCtrl::IsCaptureIdTable(void)

{
  (*(code *)PTR_IsCaptureIdTable_0004c160)();
  return;
}


/* 0001f958 */

void __thiscall
MprCtrl::_MediaInfo::GetMediaIdList(_MediaInfo *this,uint param_1,uint *param_2,uint *param_3)

{
  (*(code *)PTR_GetMediaIdList_0004c164)(this);
  return;
}


/* 0001f964 */

void __thiscall EventSwitcher::DeleteInstance(EventSwitcher *this,void *param_1)

{
  (*(code *)PTR_DeleteInstance_0004c168)(this);
  return;
}


/* 0001f970 */

void MprCtrl::SetFixedArea(uint param_1,uint param_2)

{
  (*(code *)PTR_SetFixedArea_0004c16c)(param_1);
  return;
}


/* 0001f97c */

void __thiscall
CapIdWrapper::Mmap(CapIdWrapper *this,MemExtent *param_1,int *param_2,MemExtent *param_3)

{
  (*(code *)PTR_Mmap_0004c170)(this);
  return;
}


/* 0001f988 */

void MprCtrl::GetDualRecCaptureCount(void)

{
  (*(code *)PTR_GetDualRecCaptureCount_0004c174)();
  return;
}


/* 0001f994 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void operator_delete__(void *param_1)

{
  (*(code *)PTR_operator_delete___0004c178)(param_1);
  return;
}


/* 0001f9a0 */

void __thiscall MprCtrlUpmEvent::UpdateMediaInhInfo(MprCtrlUpmEvent *this)

{
  (*(code *)PTR_UpdateMediaInhInfo_0004c17c)(this);
  return;
}


/* 0001f9ac */

void UtilList::RemoveCellFromList(_utlList *param_1,_utlCell *param_2)

{
  (*(code *)PTR_RemoveCellFromList_0004c180)(param_1);
  return;
}


/* 0001f9c8 */

void __thiscall StateMgr::UpdateCurrentState(StateMgr *this,uint param_1)

{
  (*(code *)PTR_UpdateCurrentState_0004c188)(this);
  return;
}


/* 0001f9d8 */

void MprCnv::Exchg_AreaInfo(AreaInfo *param_1,AreaInfo *param_2)

{
  (*(code *)PTR_Exchg_AreaInfo_0004c18c)(param_1);
  return;
}


/* 0001f9f4 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MprIf::NewDvdDcfMMgr(DvdDcfCreateParam *param_1,ulong *param_2)

{
  (*(code *)PTR_NewDvdDcfMMgr_0004c194)(param_1);
  return;
}


/* 0001fa00 */

void __thiscall MprCtrlUpmEvent::rsrcInfo::Init(rsrcInfo *this)

{
  (*(code *)PTR_Init_0004c198)(this);
  return;
}


/* 0001fa0c */

void UpmWrapper::OFF_TYPE_CNV(int param_1,OffType *param_2)

{
  (*(code *)PTR_OFF_TYPE_CNV_0004c19c)(param_1);
  return;
}


/* 0001fa18 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MprIf::NewBgmMMgr(BgmCreateParam *param_1,ulong *param_2)

{
  (*(code *)PTR_NewBgmMMgr_0004c1a0)(param_1);
  return;
}


/* 0001fa24 */

void __cxa_throw(void)

{
  (*(code *)PTR___cxa_throw_0004c1a4)();
  return;
}


/* 0001fa30 */

void MprCtrl::GetStillSizeTable(void)

{
  (*(code *)PTR_GetStillSizeTable_0004c1a8)();
  return;
}


/* 0001fa3c */

void MprCtrl::GetSupportMedia(void)

{
  (*(code *)PTR_GetSupportMedia_0004c1ac)();
  return;
}


/* 0001fa48 */

void __thiscall MprCtrl::_MediaInfo::GetMediaId(_MediaInfo *this,uint param_1)

{
  (*(code *)PTR_GetMediaId_0004c1b0)(this);
  return;
}


/* 0001fa54 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MonCtrl::GetFlagPtr(void)

{
  (*(code *)PTR_GetFlagPtr_0004c1b4)();
  return;
}


/* 0001fa60 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::ParamStd_Template<unsigned_short,(MWF::Param::Type)6>::GetValue(void)

{
  (*(code *)PTR_GetValue_0004c1b8)();
  return;
}


/* 0001fa6c */

void MprCtrl::SetSelfCheckLog(bool param_1)

{
  (*(code *)PTR_SetSelfCheckLog_0004c1bc)(param_1);
  return;
}


/* 0001fa78 */

void MprCtrl::CnvDeviceType(void)

{
  (*(code *)PTR_CnvDeviceType_0004c1c0)();
  return;
}


/* 0001fa84 */

void __thiscall MprCtrl::_MediaInfo::GetDeviceType(_MediaInfo *this,uint param_1)

{
  (*(code *)PTR_GetDeviceType_0004c1c4)(this);
  return;
}


/* 0001fa90 */

void __thiscall CapIdWrapper::SendCapIdTblCommand(CapIdWrapper *this,uint param_1)

{
  (*(code *)PTR_SendCapIdTblCommand_0004c1c8)(this);
  return;
}


/* 0001faac */

void MprCnv::Exchg_GPSDateStamp(GPSDateStamp *param_1,GPSDateStamp *param_2)

{
  (*(code *)PTR_Exchg_GPSDateStamp_0004c1d0)(param_1);
  return;
}


/* 0001fab8 */

void __thiscall MWF::ObjMsg::~ObjMsg(void *this)

{
  (*(code *)PTR__ObjMsg_0004c1d4)(this);
  return;
}


/* 0001fac4 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::EventIdFactory::GetId(uint param_1,uint *param_2)

{
  (*(code *)PTR_GetId_0004c1d8)(param_1);
  return;
}


/* 0001fad0 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MprIf::SetCreateParam_RecTcUbParam(bool param_1)

{
  (*(code *)PTR_SetCreateParam_RecTcUbParam_0004c1dc)(param_1);
  return;
}


/* 0001faec */

void __thiscall
EventSwitcher::Callback
          (EventSwitcher *this,_CallbackEntry *param_1,uint param_2,void *param_3,uint param_4)

{
  (*(code *)PTR_Callback_0004c1e4)(this);
  return;
}


/* 0001faf8 */

void __cxa_end_catch(void)

{
  (*(code *)PTR___cxa_end_catch_0004c1e8)();
  return;
}


/* 0001fb08 */

void MemUtil::MemCpy8(void *param_1,void *param_2,int param_3)

{
  (*(code *)PTR_MemCpy8_0004c1ec)(param_1);
  return;
}


/* 0001fb14 */

void __thiscall MprCtrl::_MprEnterInfo::Acquire(_MprEnterInfo *this,uint param_1)

{
  (*(code *)PTR_Acquire_0004c1f0)(this);
  return;
}


/* 0001fb20 */

void MprCtrlMcmd::GetMonMsg(void)

{
  (*(code *)PTR_GetMonMsg_0004c1f4)();
  return;
}


/* 0001fb3c */

void osal_dynamic_id(void)

{
  (*(code *)PTR_osal_dynamic_id_0004c1fc)();
  return;
}


/* 0001fb48 */

void MprCtrlLog::SetUnitTypeLog(uchar param_1,uint param_2,ushort param_3)

{
  (*(code *)PTR_SetUnitTypeLog_0004c200)(param_1,param_2,param_3);
  return;
}


/* 0001fb54 */

void __thiscall MprCtrlStillMgr::GetStillDataTableNum(MprCtrlStillMgr *this)

{
  (*(code *)PTR_GetStillDataTableNum_0004c204)(this);
  return;
}


/* 0001fb60 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MprIf::NewUsbAviMMgr(UsbAviCreateParam *param_1,ulong *param_2)

{
  (*(code *)PTR_NewUsbAviMMgr_0004c208)(param_1);
  return;
}


/* 0001fb6c */

void DmmAccessPLA::SetExtListPackHeaderStatus(void *param_1,ushort param_2,ushort param_3)

{
  (*(code *)PTR_SetExtListPackHeaderStatus_0004c20c)(param_1,param_2,param_3);
  return;
}


/* 0001fb78 */

void __aeabi_idivmod(void)

{
  (*(code *)PTR___aeabi_idivmod_0004c210)();
  return;
}


/* 0001fb84 */

void MprCtrl::GetMediaInfo(uint param_1,_MediaConfigInfo *param_2)

{
  (*(code *)PTR_GetMediaInfo_0004c214)(param_1);
  return;
}


/* 0001fb90 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int munmap(void *__addr,size_t __len)

{
  int iVar1;
  
  iVar1 = (*(code *)PTR_munmap_0004c218)(__addr);
  return iVar1;
}


/* 0001fb9c */

void __thiscall MWF::RsrcMgr::RsrcMgr(void)

{
  (*(code *)PTR_RsrcMgr_0004c21c)();
  return;
}


/* 0001fba8 */

void DmmAccess::DmmShare(uint param_1,ushort param_2)

{
  (*(code *)PTR_DmmShare_0004c220)(param_1,param_2);
  return;
}


/* 0001fbb4 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MprIf::NewSsdAviMMgr(SsdAviCreateParam *param_1,ulong *param_2)

{
  (*(code *)PTR_NewSsdAviMMgr_0004c224)(param_1);
  return;
}


/* 0001fbc0 */

void MprCtrl::GetCreateMMgrType(_MediaConfigInfo *param_1)

{
  (*(code *)PTR_GetCreateMMgrType_0004c228)(param_1);
  return;
}


/* 0001fbcc */

void __thiscall MWF::InhMgr::~InhMgr(InhMgr *this)

{
  (*(code *)PTR__InhMgr_0004c22c)(this);
  return;
}


/* 0001fbd8 */

void __thiscall MprCtrl::_MediaInfo::RemoveDsysId(_MediaInfo *this,uint param_1)

{
  (*(code *)PTR_RemoveDsysId_0004c230)(this);
  return;
}


/* 0001fbe4 */

void __thiscall MWF::ObjLock::Lock(ObjLock *this)

{
  (*(code *)PTR_Lock_0004c234)(this);
  return;
}


/* 0001fc00 */

void MprCtrl::IsInternalFlashAviSupport(void)

{
  (*(code *)PTR_IsInternalFlashAviSupport_0004c23c)();
  return;
}


/* 0001fc0c */

void DmmAccess::Quit(void)

{
  (*(code *)PTR_Quit_0004c240)();
  return;
}


/* 0001fc18 */

void MprCnv::Exchg_GPSDateStamp(GPSDateStamp *param_1,GPSDateStamp *param_2)

{
  (*(code *)PTR_Exchg_GPSDateStamp_0004c244)(param_1);
  return;
}


/* 0001fc24 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::ParamStd_Template<bool,(MWF::Param::Type)1>::GetValue(void)

{
  (*(code *)PTR_GetValue_0004c248)();
  return;
}


/* 0001fc30 */

void UtilStillSize::SearchStillSize(void)

{
  (*(code *)PTR_SearchStillSize_0004c24c)();
  return;
}


/* 0001fc3c */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::UInt64::GetValue(void)

{
  (*(code *)PTR_GetValue_0004c250)();
  return;
}


/* 0001fc48 */

void __cxa_begin_catch(void)

{
  (*(code *)PTR___cxa_begin_catch_0004c254)();
  return;
}


/* 0001fc54 */

void UtilStillSize::GetContentAspect(void)

{
  (*(code *)PTR_GetContentAspect_0004c258)();
  return;
}


/* 0001fc60 */

void __thiscall EventHandlerWrapper::~EventHandlerWrapper(EventHandlerWrapper *this)

{
  (*(code *)PTR__EventHandlerWrapper_0004c25c)(this);
  return;
}


/* 0001fc70 */

void __thiscall MprCtrlInputEvent::SendInputEvent(MprCtrlInputEvent *this,int param_1,int param_2)

{
  (*(code *)PTR_SendInputEvent_0004c260)(this);
  return;
}


/* 0001fc7c */

void __thiscall MprCtrlInputEvent::Init(MprCtrlInputEvent *this,uint param_1)

{
  (*(code *)PTR_Init_0004c264)(this);
  return;
}


/* 0001fc88 */

void __thiscall UpmWrapper::~UpmWrapper(UpmWrapper *this)

{
  (*(code *)PTR__UpmWrapper_0004c268)(this);
  return;
}


/* 0001fc94 */

void UpmWrapper::CONNECT_STAT_CNV(int param_1,ConnectStat *param_2)

{
  (*(code *)PTR_CONNECT_STAT_CNV_0004c26c)(param_1);
  return;
}


/* 0001fcb0 */

void UtilStillSize::SearchApproxStillSize(void)

{
  (*(code *)PTR_SearchApproxStillSize_0004c274)();
  return;
}


/* 0001fcbc */

void __thiscall MWF::EventHandler::~EventHandler(EventHandler *this)

{
  (*(code *)PTR__EventHandler_0004c278)(this);
  return;
}


/* 0001fcc8 */

void Backup_read_4Byte(void)

{
  (*(code *)PTR_Backup_read_4Byte_0004c27c)();
  return;
}


/* 0001fcd4 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MprIf::NewMsAviMMgr(MsAviCreateParam *param_1,ulong *param_2)

{
  (*(code *)PTR_NewMsAviMMgr_0004c280)(param_1);
  return;
}


/* 0001fce0 */

void __thiscall
MprCtrlStillMgr::CalcStillData_S3
          (MprCtrlStillMgr *this,int param_1,int param_2,int param_3,int param_4,uint param_5,
          uint *param_6,uint *param_7)

{
  (*(code *)PTR_CalcStillData_S3_0004c284)(this);
  return;
}


/* 0001fcec */

void DmmAccessPLA::GetExtListPackSize(uint param_1)

{
  (*(code *)PTR_GetExtListPackSize_0004c288)(param_1);
  return;
}


/* 0001fcf8 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MonLib::MonCmdAdd(char *param_1,_func_bool_int_char_ptr_ptr *param_2,char *param_3)

{
  (*(code *)PTR_MonCmdAdd_0004c28c)(param_1);
  return;
}


/* 0001fd04 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::EventSender::SetEventReceiver(EventReceiver *param_1)

{
  (*(code *)PTR_SetEventReceiver_0004c290)(param_1);
  return;
}


/* 0001fd10 */

void MprObjectUtil::MwfUInt32(ObjMsg *param_1,uint param_2)

{
  (*(code *)PTR_MwfUInt32_0004c294)(param_1);
  return;
}


/* 0001fd1c */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MonCtrl::ConPutMessageHeader(void)

{
  (*(code *)PTR_ConPutMessageHeader_0004c298)();
  return;
}


/* 0001fd28 */

void __gxx_personality_v0(void)

{
  (*(code *)PTR___gxx_personality_v0_0004c29c)();
  return;
}


/* 0001fd34 */

void DmmAccessPLA::GetExtListPackAdrsOnPackHeader(void *param_1,uint param_2)

{
  (*(code *)PTR_GetExtListPackAdrsOnPackHeader_0004c2a0)(param_1);
  return;
}


/* 0001fd40 */

void UtilList::GetNextCell(_utlCell *param_1)

{
  (*(code *)PTR_GetNextCell_0004c2a4)(param_1);
  return;
}


/* 0001fd4c */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::ObjMsg::GetMessageId(void)

{
  (*(code *)PTR_GetMessageId_0004c2a8)();
  return;
}


/* 0001fd58 */

void MWF::EventHandler::SetEventMessage(void)

{
  (*(code *)PTR_SetEventMessage_0004c2ac)();
  return;
}


/* 0001fd64 */

void __thiscall MprCtrlStillMgr::GetBackupStillSize(MprCtrlStillMgr *this)

{
  (*(code *)PTR_GetBackupStillSize_0004c2b0)(this);
  return;
}


/* 0001fd70 */

void MprCtrl::IsTcUbSupport(void)

{
  (*(code *)PTR_IsTcUbSupport_0004c2b4)();
  return;
}


/* 0001fd7c */

void MprCtrl::IsSerialNumberRecSupport(void)

{
  (*(code *)PTR_IsSerialNumberRecSupport_0004c2b8)();
  return;
}


/* 0001fd88 */

void MprCnv::Exchg_JpgInfo(JpgInfo *param_1,JpgInfo *param_2)

{
  (*(code *)PTR_Exchg_JpgInfo_0004c2bc)(param_1);
  return;
}


/* 0001fd94 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MprIf::Create(CreateParam *param_1,MprIf **param_2,bool param_3)

{
  (*(code *)PTR_Create_0004c2c0)(param_1,param_2,param_3);
  return;
}


/* 0001fda0 */

void __thiscall MprCtrl::_MediaInfo::~_MediaInfo(_MediaInfo *this)

{
  (*(code *)PTR___MediaInfo_0004c2c4)(this);
  return;
}


/* 0001fdac */

void __thiscall MprCtrlStillMgr::IsRecordingSCN(MprCtrlStillMgr *this,uint param_1)

{
  (*(code *)PTR_IsRecordingSCN_0004c2c8)(this);
  return;
}


/* 0001fdb8 */

void DmmAccessPLA::GetExtListPackHeaderSize(uint param_1)

{
  (*(code *)PTR_GetExtListPackHeaderSize_0004c2cc)(param_1);
  return;
}


/* 0001fdc4 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::Int64::GetValue(void)

{
  (*(code *)PTR_GetValue_0004c2d0)();
  return;
}


/* 0001fdd0 */

void osal_snd_sync_direct(void)

{
  (*(code *)PTR_osal_snd_sync_direct_0004c2d4)();
  return;
}


/* 0001fddc */

void MprCnv::Exchg_LongitudeRef(LongitudeRef *param_1,LongitudeRef *param_2)

{
  (*(code *)PTR_Exchg_LongitudeRef_0004c2d8)(param_1);
  return;
}


/* 0001fde8 */

void UtilList::AddCellToList(_utlList *param_1,_utlCell *param_2)

{
  (*(code *)PTR_AddCellToList_0004c2dc)(param_1);
  return;
}


/* 0001fdf4 */

void DmmAccess::DmmCloseAndFree(ushort param_1)

{
  (*(code *)PTR_DmmCloseAndFree_0004c2e0)(param_1);
  return;
}


/* 0001fe10 */

void MprCtrl::CreateDsys(uint param_1)

{
  (*(code *)PTR_CreateDsys_0004c2e8)(param_1);
  return;
}


/* 0001fe1c */

void DmmAccess::AllocDmmMemory(int param_1,ushort *param_2)

{
  (*(code *)PTR_AllocDmmMemory_0004c2ec)(param_1);
  return;
}


/* 0001fe28 */

void DmmAccess::GetModeIdName(int param_1)

{
  (*(code *)PTR_GetModeIdName_0004c2f0)(param_1);
  return;
}


/* 0001fe34 */

void DmmAccess::Init(bool param_1)

{
  (*(code *)PTR_Init_0004c2f4)(param_1);
  return;
}


/* 0001fe40 */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MprIf::SetCreateParam_MultiMovieRec(bool param_1)

{
  (*(code *)PTR_SetCreateParam_MultiMovieRec_0004c2f8)(param_1);
  return;
}


/* 0001fe4c */

void __thiscall MprCtrlInputEvent::MprCtrlInputEvent(MprCtrlInputEvent *this)

{
  (*(code *)PTR_MprCtrlInputEvent_0004c2fc)(this);
  return;
}


/* 0001fe58 */

void __thiscall MprCtrlUpmEvent::RegisterBusPowerEvent(MprCtrlUpmEvent *this)

{
  (*(code *)PTR_RegisterBusPowerEvent_0004c300)(this);
  return;
}


/* 0001fe64 */

void StrUtil::StrNCat(char *param_1,char *param_2,int param_3)

{
  (*(code *)PTR_StrNCat_0004c304)(param_1);
  return;
}


/* 0001fe74 */

void MprCnv::Exchg_DegMinSec(DegMinSec *param_1,DegMinSec *param_2)

{
  (*(code *)PTR_Exchg_DegMinSec_0004c308)(param_1);
  return;
}


/* 0001fe80 */

void __thiscall
UpmWrapper::RegisterCallBackForBatteryLevel
          (UpmWrapper *this,uint param_1,_func_void_void_ptr_int_void_ptr_uint *param_2,
          void *param_3)

{
  (*(code *)PTR_RegisterCallBackForBatteryLevel_0004c30c)(this);
  return;
}


/* 0001fe8c */

void __cxa_finalize(void)

{
  (*(code *)PTR___cxa_finalize_0004c310)();
  return;
}


/* 0001fe98 */

void osal_snd_sync_msg(void)

{
  (*(code *)PTR_osal_snd_sync_msg_0004c314)();
  return;
}


/* 0001fea4 */

void __thiscall UpmWrapper::ClearCallBackForHeatAlert(UpmWrapper *this)

{
  (*(code *)PTR_ClearCallBackForHeatAlert_0004c318)(this);
  return;
}


/* 0001feb0 */

void __thiscall MprCtrlUpmEvent::UpdateInhInfo(void)

{
  (*(code *)PTR_UpdateInhInfo_0004c31c)();
  return;
}


/* 0001febc */

void MprCtrlMcmd::Init(void)

{
  (*(code *)PTR_Init_0004c320)();
  return;
}


/* 0001fec8 */

void MprCnv::Exchg_GpsMeasureMode(GpsMeasureMode *param_1,GpsMeasureMode *param_2)

{
  (*(code *)PTR_Exchg_GpsMeasureMode_0004c324)(param_1);
  return;
}


/* 0001fed4 */

void MprCtrlMcmd::GetMonErr(void)

{
  (*(code *)PTR_GetMonErr_0004c328)();
  return;
}


/* 0001fee0 */

void DmmAccess::BufFree(uchar *param_1)

{
  (*(code *)PTR_BufFree_0004c32c)(param_1);
  return;
}


/* 0001feec */

void __thiscall MprCtrlStill::_StillSizeTable::_StillSizeTable(_StillSizeTable *this)

{
  (*(code *)PTR__StillSizeTable_0004c330)(this);
  return;
}


/* 0001fef8 */

void UtimeWrapper::GetSysCnt(void)

{
  (*(code *)PTR_GetSysCnt_0004c334)();
  return;
}


/* 0001ff04 */

void MprCtrl::GetStillDataInfo
               (int param_1,int param_2,int param_3,int param_4,int param_5,int param_6,
               StillDataInfo *param_7)

{
  (*(code *)PTR_GetStillDataInfo_0004c338)(param_1);
  return;
}


/* 0001ff10 */

void __thiscall StatMgr::UpdateCurrentState(StatMgr *this,uint param_1)

{
  (*(code *)PTR_UpdateCurrentState_0004c33c)(this);
  return;
}


/* 0001ff20 */

void osal_free_msg(void)

{
  (*(code *)PTR_osal_free_msg_0004c340)();
  return;
}


/* 0001ff2c */

void __thiscall MprCtrlStillMgr::Exchg_Byte(MprCtrlStillMgr *this,int param_1)

{
  (*(code *)PTR_Exchg_Byte_0004c344)(this);
  return;
}


/* 0001ff38 */

void processEntry entry(void)

{
  if (*(int *)(DAT_0001ff48 + 0x1ff40 + DAT_0001ff4c) == 0) {
    return;
  }
  (*(code *)PTR___gmon_start___0004bd70)();
  return;
}


/* 0001ff50 */

void _FINI_0(void)

{
  if (*(char *)(DAT_0001ff7c + 0x1ff58) == '\0') {
    if (*(int *)(DAT_0001ff80 + 0x1ff5e + DAT_0001ff84) != 0) {
      __cxa_finalize(*(undefined4 *)(DAT_0001ff88 + 0x1ff6a));
    }
    *(undefined1 *)(DAT_0001ff8c + 0x1ff78) = 1;
  }
  return;
}


/* 0001ff90 */

void _INIT_0(void)

{
  code *pcVar1;
  
  if (*(int *)(DAT_0001ffa8 + 0x1ff98) != 0) {
    pcVar1 = *(code **)(DAT_0001ffac + 0x1ff9e + DAT_0001ffb0);
    if (pcVar1 != (code *)0x0) {
      (*pcVar1)();
    }
  }
  return;
}


/* 0001ffb4 */

void FUN_0001ffb4(int param_1,undefined4 param_2)

{
  *(undefined4 *)(param_1 + -4) = param_2;
  return;
}


/* 0001ffbe */

void FUN_0001ffbe(undefined1 *param_1)

{
  *param_1 = 0;
  *(undefined4 *)(param_1 + 4) = 0;
  *(undefined4 *)(param_1 + 8) = 0xffffffff;
  *(undefined4 *)(param_1 + 0xc) = 0;
  return;
}


/* 0001ffd4 */

int FUN_0001ffd4(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 *param_4,
                undefined4 param_5)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 *local_24 [2];
  
  iVar1 = osal_valloc_msg_wait(DAT_0002003c,local_24,0x10,1);
  if (iVar1 == 0) {
    FUN_0001ffb4(local_24[0],param_5);
    uVar2 = DAT_0002003c;
    *local_24[0] = param_1;
    local_24[0][1] = param_2;
    local_24[0][2] = 3;
    local_24[0][3] = param_3;
    iVar1 = osal_snd_sync_msg(uVar2);
    if ((iVar1 == 0) && (param_4 != (undefined4 *)0x0)) {
      *param_4 = *local_24[0];
      param_4[1] = local_24[0][1];
      uVar2 = local_24[0][3];
      param_4[2] = local_24[0][2];
      param_4[3] = uVar2;
    }
    osal_free_msg(DAT_0002003c,local_24[0]);
  }
  return iVar1;
}


/* 00020040 */

/* MWF::ObjLock::Lock() */

void __thiscall MWF::ObjLock::Lock(ObjLock *this)

{
  (*(code *)PTR_pthread_mutex_lock_0004bf2c)(this + 4);
  return;
}


/* 0002004e */

/* MWF::ObjLock::Unlock() */

void __thiscall MWF::ObjLock::Unlock(ObjLock *this)

{
  (*(code *)PTR_pthread_mutex_unlock_0004bed0)(this + 4);
  return;
}


/* 0002005c */

/* MprCtrlStill::_StillSizeTable::_StillSizeTable() */

void __thiscall MprCtrlStill::_StillSizeTable::_StillSizeTable(_StillSizeTable *this)

{
  int iVar1;
  int iVar2;
  
  iVar1 = 0;
  do {
    *(undefined2 *)(this + iVar1) = 0;
    iVar2 = iVar1 + 8;
    *(undefined2 *)(this + iVar1 + 2) = 0;
    *(undefined4 *)(this + iVar1 + 4) = 0;
    iVar1 = iVar2;
  } while (iVar2 != 0x318);
  return;
}


/* 00020076 */

/* MprCtrlStillMgr::GetStillSizeTable() */

undefined4 __thiscall MprCtrlStillMgr::GetStillSizeTable(MprCtrlStillMgr *this)

{
  return *(undefined4 *)(this + 4);
}


/* 0002007e */

/* MprCtrlStillMgr::GetStillDataTable() */

undefined4 __thiscall MprCtrlStillMgr::GetStillDataTable(MprCtrlStillMgr *this)

{
  return *(undefined4 *)(this + 8);
}


/* 00020086 */

/* MprCtrlStillMgr::GetStillDataTableNum() */

undefined4 __thiscall MprCtrlStillMgr::GetStillDataTableNum(MprCtrlStillMgr *this)

{
  return *(undefined4 *)(this + 0xc);
}


/* 0002008e */

/* MprCtrl::_MediaInfo::_MediaInfo() */

_MediaInfo * __thiscall MprCtrl::_MediaInfo::_MediaInfo(_MediaInfo *this)

{
  int iVar1;
  _MediaInfo *p_Var2;
  
  MWF::ObjLock::ObjLock((ObjLock *)(this + 0x70));
  p_Var2 = this;
  for (iVar1 = 0; iVar1 != 5; iVar1 = iVar1 + 1) {
    *p_Var2 = (_MediaInfo)0x0;
    *(undefined4 *)(p_Var2 + 4) = 0;
    *(undefined4 *)(p_Var2 + 0xc) = 0;
    *(undefined4 *)(p_Var2 + 8) = 0xffffffff;
    p_Var2 = p_Var2 + 0x10;
  }
  this[0x50] = (_MediaInfo)0x0;
  *(undefined4 *)(this + 0x54) = 0;
  *(undefined4 *)(this + 0x58) = 0xffffffff;
  *(undefined4 *)(this + 0x5c) = 0;
  this[0x60] = (_MediaInfo)0x0;
  *(undefined4 *)(this + 100) = 0;
  *(undefined4 *)(this + 0x68) = 0xffffffff;
  *(undefined4 *)(this + 0x6c) = 0;
  return this;
}


/* 000200d6 */

/* MprCtrl::_MediaInfo::Init() */

void __thiscall MprCtrl::_MediaInfo::Init(_MediaInfo *this)

{
  int iVar1;
  int iVar2;
  
  iVar2 = 0;
  do {
    iVar1 = iVar2 * 0x10;
    iVar2 = iVar2 + 1;
    FUN_0001ffbe(this + iVar1);
  } while (iVar2 != 5);
  FUN_0001ffbe(this + 0x50);
  FUN_0001ffbe(this + 0x60);
  return;
}


/* 00020100 */

/* MprCtrl::_MediaInfo::RemoveMMgrId(unsigned int) */

undefined4 __thiscall MprCtrl::_MediaInfo::RemoveMMgrId(_MediaInfo *this,uint param_1)

{
  _MediaInfo *p_Var1;
  _MediaInfo *p_Var2;
  int iVar3;
  
  iVar3 = 0;
  p_Var2 = this;
  do {
    p_Var1 = p_Var2 + 8;
    p_Var2 = p_Var2 + 0x10;
    if (*(uint *)p_Var1 == param_1) {
      FUN_0001ffbe(this + iVar3 * 0x10);
      return 0;
    }
    iVar3 = iVar3 + 1;
  } while (iVar3 != 5);
  return 0xffffffff;
}


/* 00020128 */

/* MprCtrl::_MediaInfo::RemoveDsysId(unsigned int) */

undefined4 __thiscall MprCtrl::_MediaInfo::RemoveDsysId(_MediaInfo *this,uint param_1)

{
  int iVar1;
  
  if (*(uint *)(this + 0x58) == param_1) {
    iVar1 = 0;
  }
  else {
    if (*(uint *)(this + 0x68) != param_1) {
      return 0xffffffff;
    }
    iVar1 = 1;
  }
  FUN_0001ffbe(this + (iVar1 + 5) * 0x10);
  return 0;
}


/* 00020152 */

/* MprCtrl::_MediaInfo::GetMediaId(unsigned int) */

undefined4 __thiscall MprCtrl::_MediaInfo::GetMediaId(_MediaInfo *this,uint param_1)

{
  int iVar1;
  
  iVar1 = 0;
  do {
    if (*(uint *)(this + iVar1 * 0x10 + 4) == param_1) {
      return *(undefined4 *)(this + iVar1 * 0x10 + 8);
    }
    iVar1 = iVar1 + 1;
  } while (iVar1 != 5);
  return 0xffffffff;
}


/* 00020172 */

/* MprCtrl::_MediaInfo::GetMMgrId(unsigned int) */

undefined4 __thiscall MprCtrl::_MediaInfo::GetMMgrId(_MediaInfo *this,uint param_1)

{
  _MediaInfo *p_Var1;
  _MediaInfo *p_Var2;
  int iVar3;
  
  iVar3 = 0;
  p_Var2 = this;
  do {
    p_Var1 = p_Var2 + 8;
    p_Var2 = p_Var2 + 0x10;
    if (*(uint *)p_Var1 == param_1) {
      return *(undefined4 *)(this + iVar3 * 0x10 + 4);
    }
    iVar3 = iVar3 + 1;
  } while (iVar3 != 5);
  return 0;
}


/* 00020194 */

/* MprCtrl::_MediaInfo::GetDsysId(unsigned int) */

undefined4 __thiscall MprCtrl::_MediaInfo::GetDsysId(_MediaInfo *this,uint param_1)

{
  int iVar1;
  
  if (*(uint *)(this + 0x58) == param_1) {
    iVar1 = 0;
  }
  else {
    if (*(uint *)(this + 0x68) != param_1) {
      return 0;
    }
    iVar1 = 1;
  }
  return *(undefined4 *)(this + (iVar1 + 5) * 0x10 + 4);
}


/* 000201b8 */

/* MprCtrl::_MediaInfo::SetMMgrId(unsigned int, MPR::DeviceType, unsigned int) */

undefined4 __thiscall
MprCtrl::_MediaInfo::SetMMgrId(_MediaInfo *this,int param_1,undefined4 param_3,undefined4 param_4)

{
  _MediaInfo *p_Var1;
  int iVar2;
  int iVar3;
  _MediaInfo *p_Var4;
  
  iVar2 = 0;
  p_Var4 = this;
  do {
    iVar3 = iVar2;
    p_Var1 = p_Var4 + 8;
    p_Var4 = p_Var4 + 0x10;
    if (*(int *)p_Var1 == param_1) {
      iVar3 = iVar3 * 0x10;
      this[iVar3] = (_MediaInfo)0x1;
      *(undefined4 *)(this + iVar3 + 4) = param_4;
      *(undefined4 *)(this + iVar3 + 0xc) = param_3;
      return 0;
    }
    iVar2 = iVar3 + 1;
  } while (iVar3 + 1 != 5);
  iVar3 = iVar3 + -4;
  p_Var4 = this;
  do {
    p_Var1 = p_Var4 + 8;
    p_Var4 = p_Var4 + 0x10;
    if (*(int *)p_Var1 == -1) {
      iVar3 = iVar3 * 0x10;
      this[iVar3] = (_MediaInfo)0x1;
      *(undefined4 *)(this + iVar3 + 4) = param_4;
      *(int *)(this + iVar3 + 8) = param_1;
      *(undefined4 *)(this + iVar3 + 0xc) = param_3;
      return 0;
    }
    iVar3 = iVar3 + 1;
  } while (iVar3 != 5);
  return 0xffffffff;
}


/* 0002020a */

/* MprCtrl::_MediaInfo::SetDsysId(unsigned int, MPR::DeviceType, unsigned int) */

undefined4 __thiscall
MprCtrl::_MediaInfo::SetDsysId(_MediaInfo *this,int param_1,undefined4 param_3,undefined4 param_4)

{
  _MediaInfo *p_Var1;
  int iVar2;
  int iVar3;
  
  if (*(int *)(this + 0x58) == param_1) {
    iVar2 = 0;
  }
  else {
    if (*(int *)(this + 0x68) != param_1) {
      if (*(int *)(this + 0x58) == -1) {
        iVar2 = 0;
      }
      else {
        if (*(int *)(this + 0x68) != -1) {
          return 0xffffffff;
        }
        iVar2 = 1;
      }
      iVar3 = (iVar2 + 5) * 0x10;
      this[iVar3] = (_MediaInfo)0x1;
      p_Var1 = this + iVar2 * 0x10;
      *(undefined4 *)(this + iVar3 + 4) = param_4;
      *(int *)(p_Var1 + 0x58) = param_1;
      goto LAB_00020254;
    }
    iVar2 = 1;
  }
  iVar3 = (iVar2 + 5) * 0x10;
  this[iVar3] = (_MediaInfo)0x1;
  p_Var1 = this + iVar2 * 0x10;
  *(undefined4 *)(this + iVar3 + 4) = param_4;
LAB_00020254:
  *(undefined4 *)(p_Var1 + 0x5c) = param_3;
  return 0;
}


/* 00020268 */

/* MprCtrl::_MediaInfo::GetDeviceType(unsigned int) */

undefined4 __thiscall MprCtrl::_MediaInfo::GetDeviceType(_MediaInfo *this,uint param_1)

{
  _MediaInfo *p_Var1;
  _MediaInfo *p_Var2;
  undefined4 uVar3;
  int iVar4;
  
  iVar4 = 0;
  p_Var2 = this;
  do {
    p_Var1 = p_Var2 + 8;
    p_Var2 = p_Var2 + 0x10;
    if (*(uint *)p_Var1 == param_1) {
      uVar3 = *(undefined4 *)(this + iVar4 * 0x10 + 0xc);
      goto LAB_00020288;
    }
    iVar4 = iVar4 + 1;
  } while (iVar4 != 5);
  uVar3 = 0;
LAB_00020288:
  if (*(uint *)(this + 0x58) == param_1) {
    iVar4 = 0;
  }
  else {
    if (*(uint *)(this + 0x68) != param_1) {
      return uVar3;
    }
    iVar4 = 1;
  }
  return *(undefined4 *)(this + iVar4 * 0x10 + 0x5c);
}


/* 000202a2 */

/* MprCtrl::_MediaInfo::GetMediaIdList(unsigned int, unsigned int*, unsigned int*) */

void __thiscall
MprCtrl::_MediaInfo::GetMediaIdList(_MediaInfo *this,uint param_1,uint *param_2,uint *param_3)

{
  uint uVar1;
  int iVar2;
  
  uVar1 = 0;
  iVar2 = 0;
  do {
    if (*(uint *)(this + 8) != 0xffffffff) {
      param_2[uVar1] = *(uint *)(this + 8);
      uVar1 = uVar1 + 1;
      if (param_1 <= uVar1) break;
    }
    iVar2 = iVar2 + 1;
    this = this + 0x10;
  } while (iVar2 != 5);
  *param_3 = uVar1;
  return;
}


/* 000202c8 */

/* MprCtrl::_MprEnterInfo::_MprEnterInfo() */

void __thiscall MprCtrl::_MprEnterInfo::_MprEnterInfo(_MprEnterInfo *this)

{
  int iVar1;
  
  iVar1 = 0;
  do {
    *(undefined4 *)(this + iVar1) = 0;
    iVar1 = iVar1 + 4;
  } while (iVar1 != 0x2c);
  return;
}


/* 000202da */

/* MprCtrl::_MprEnterInfo::Init() */

void __thiscall MprCtrl::_MprEnterInfo::Init(_MprEnterInfo *this)

{
  int iVar1;
  
  iVar1 = 0;
  do {
    *(undefined4 *)(this + iVar1) = 0;
    iVar1 = iVar1 + 4;
  } while (iVar1 != 0x2c);
  return;
}


/* 000202ec */

/* MprCtrl::_MprEnterInfo::Acquire(unsigned int) */

void __thiscall MprCtrl::_MprEnterInfo::Acquire(_MprEnterInfo *this,uint param_1)

{
  *(int *)(this + param_1 * 4) = *(int *)(this + param_1 * 4) + 1;
  return;
}


/* 000202fe */

/* MprCtrl::_MprEnterInfo::Release(unsigned int) */

void __thiscall MprCtrl::_MprEnterInfo::Release(_MprEnterInfo *this,uint param_1)

{
  *(int *)(this + param_1 * 4) = *(int *)(this + param_1 * 4) + -1;
  return;
}


/* 00020310 */

/* MprCtrl::_MprEnterInfo::Get(unsigned int) */

undefined4 __thiscall MprCtrl::_MprEnterInfo::Get(_MprEnterInfo *this,uint param_1)

{
  return *(undefined4 *)(this + param_1 * 4);
}


/* 0002031a */

/* MprCtrl::_RecLineTable::_RecLineTable() */

void __thiscall MprCtrl::_RecLineTable::_RecLineTable(_RecLineTable *this)

{
  *(undefined4 *)this = 0xffffffff;
  *(undefined4 *)(this + 4) = 0xffffffff;
  *(undefined4 *)(this + 8) = 0xffffffff;
  return;
}


/* 0002032a */

/* MprCtrl::_RecLineTable::Init() */

void __thiscall MprCtrl::_RecLineTable::Init(_RecLineTable *this)

{
  *(undefined4 *)this = 0xffffffff;
  *(undefined4 *)(this + 4) = 0xffffffff;
  *(undefined4 *)(this + 8) = 0xffffffff;
  return;
}


/* 0002033a */

/* MprCtrl::_RecLineTable::GetLine(unsigned int) */

int __thiscall MprCtrl::_RecLineTable::GetLine(_RecLineTable *this,uint param_1)

{
  int iVar1;
  
  if (*(int *)this == -1) {
    iVar1 = 0;
  }
  else if (*(int *)(this + 4) == -1) {
    iVar1 = 1;
  }
  else {
    if (*(int *)(this + 8) != -1) {
      return -1;
    }
    iVar1 = 2;
  }
  *(uint *)(this + iVar1 * 4) = param_1;
  return iVar1;
}


/* 0002036e */

/* MprCtrl::_RecLineTable::Remove(unsigned int) */

void __thiscall MprCtrl::_RecLineTable::Remove(_RecLineTable *this,uint param_1)

{
  if (param_1 < 3) {
    *(undefined4 *)(this + param_1 * 4) = 0xffffffff;
  }
  return;
}


/* 00020382 */

/* MprCtrl::_RecLineTable::GetMediaId(unsigned int) */

undefined4 __thiscall MprCtrl::_RecLineTable::GetMediaId(_RecLineTable *this,uint param_1)

{
  undefined4 uVar1;
  
  if (param_1 < 3) {
    uVar1 = *(undefined4 *)(this + param_1 * 4);
  }
  else {
    uVar1 = 0xffffffff;
  }
  return uVar1;
}


/* 00020396 */

/* MemUtil::MemSet8(void*, unsigned char, int) */

void MemUtil::MemSet8(void *param_1,uchar param_2,int param_3)

{
  (*(code *)PTR_memset_0004bde4)(param_1,param_2);
  return;
}


/* 000203a2 */

/* MemUtil::MemCpy8(void*, void const*, int) */

void MemUtil::MemCpy8(void *param_1,void *param_2,int param_3)

{
  (*(code *)PTR_memcpy_0004bf5c)(param_1);
  return;
}


/* 000203ae */

/* MprCtrl::_MediaInfo::~_MediaInfo() */

_MediaInfo * __thiscall MprCtrl::_MediaInfo::~_MediaInfo(_MediaInfo *this)

{
  MWF::ObjLock::~ObjLock((ObjLock *)(this + 0x70));
  return this;
}


/* 000203c0 */

/* MprCtrl::CreateStillSizeList(MPR::StillSize*, int*) */

void MprCtrl::CreateStillSizeList(StillSize *param_1,int *param_2)

{
  ushort uVar1;
  bool bVar2;
  void *pvVar3;
  char *pcVar4;
  uint uVar5;
  uint uVar6;
  int iVar7;
  undefined4 *puVar8;
  uint uVar9;
  uint uVar10;
  int iVar11;
  uint uVar12;
  _StillSizeTable local_348 [2];
  ushort local_346 [395];
  undefined4 local_30;
  undefined4 local_2c;
  
  iVar7 = DAT_000204f4;
  MprCtrlStill::_StillSizeTable::_StillSizeTable(local_348);
  iVar11 = 0;
  local_2c = 0;
  puVar8 = *(undefined4 **)(iVar7 + 0x203dc + DAT_000204f8);
  MonCtrl::ConPrintfMessage((char *)*puVar8,DAT_000204fc + 0x203f0);
  MprCtrlLog::SetStartApiLog('\x04',0x2fe);
  pvVar3 = (void *)MprCtrlStillMgr::GetStillSizeTable
                             ((MprCtrlStillMgr *)**(undefined4 **)(iVar7 + 0x203dc + DAT_00020500));
  MemUtil::MemCpy8(local_348,pvVar3,0x318);
  uVar9 = 0;
  do {
    uVar1 = *(ushort *)((int)local_346 + iVar11 + -2);
    uVar5 = (uint)uVar1;
    uVar10 = uVar9;
    if (uVar5 != 0) {
      uVar6 = (uint)*(ushort *)((int)local_346 + iVar11);
      if (uVar6 != 0) {
        iVar7 = 0;
        bVar2 = false;
        for (uVar12 = 0; uVar12 < uVar9; uVar12 = uVar12 + 1) {
          if ((*(uint *)(param_1 + iVar7) == uVar5) && (*(uint *)(param_1 + iVar7 + 4) == uVar6)) {
            bVar2 = true;
          }
          iVar7 = iVar7 + 0xc;
        }
        if (!bVar2) {
          local_2c = CONCAT22(*(ushort *)((int)local_346 + iVar11),uVar1);
          iVar7 = uVar9 * 0xc;
          *(uint *)(param_1 + iVar7) = uVar5;
          *(uint *)(param_1 + iVar7 + 4) = uVar6;
          local_30 = UtilStillSize::GetContentAspect(local_2c);
          MprCtrlCnv::Exchg_StillAspect((SAspect *)(param_1 + iVar7 + 8),(ContentAspect *)&local_30)
          ;
          uVar10 = uVar9 + 1;
          MonCtrl::ConPrintfMessage((char *)*puVar8,DAT_00020504 + 0x2048e,uVar9);
          MonCtrl::ConPrintfMessage
                    ((char *)*puVar8,DAT_00020508 + 0x2049a,*(undefined4 *)(param_1 + iVar7));
          MonCtrl::ConPrintfMessage
                    ((char *)*puVar8,DAT_0002050c + 0x204a8,*(undefined4 *)(param_1 + iVar7 + 4));
          MonCtrl::ConPrintfMessage
                    ((char *)*puVar8,DAT_00020510 + 0x204b6,*(undefined4 *)(param_1 + iVar7 + 8));
          MonCtrl::ConPrintfMessage((char *)*puVar8,DAT_00020514 + 0x204c4);
        }
      }
    }
    iVar7 = DAT_00020518;
    iVar11 = iVar11 + 8;
    uVar9 = uVar10;
  } while (iVar11 != 0x318);
  pcVar4 = (char *)*puVar8;
  *param_2 = uVar10;
  MonCtrl::ConPrintfMessage(pcVar4,iVar7 + 0x204da);
  MprCtrlLog::SetEndApiLog('\x04',0,0x329);
  return;
}


/* 0002051c */

/* MprCtrl::CreateMMgrExec(unsigned int, MprCtrl::CreateIfType) */

uint MprCtrl::CreateMMgrExec(uint param_1,int param_2)

{
  _func_void_ulong_ulong_void_ptr_ulong_void_ptr *p_Var1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  undefined4 *puVar6;
  uint uVar7;
  int *piVar8;
  _MediaInfo *p_Var9;
  ulong *puVar10;
  ulong uVar11;
  undefined4 local_1cc;
  _MediaConfigInfo a_Stack_1c4 [4];
  char acStack_1c0 [24];
  int local_1a8;
  byte local_17e;
  char local_13e;
  byte local_13c;
  uint local_100 [3];
  char *local_f4;
  char *local_f0;
  undefined4 local_ec;
  undefined4 local_e8;
  undefined1 local_e4;
  undefined1 local_e3;
  undefined1 local_e2;
  undefined1 local_e1;
  uint local_e0 [3];
  char *local_d4;
  char *local_d0;
  undefined4 local_cc;
  undefined4 local_c8;
  undefined1 local_c4;
  undefined1 local_c3;
  undefined1 local_c2;
  undefined1 local_c1;
  uint local_c0;
  undefined4 local_bc;
  undefined4 local_b8;
  char *local_b4;
  char *local_b0;
  undefined4 local_ac;
  undefined4 local_a8;
  undefined1 local_a4;
  undefined1 local_a3;
  char local_a2;
  undefined1 local_a1;
  uint local_a0 [3];
  char *local_94;
  char *local_90;
  undefined4 local_8c;
  undefined4 local_88;
  undefined1 local_84;
  undefined1 local_83;
  undefined1 local_82;
  undefined1 local_81;
  uint local_80 [3];
  char *local_74;
  char *local_70;
  undefined4 local_6c;
  undefined4 local_68;
  undefined1 local_64;
  undefined1 local_63;
  undefined1 local_62;
  undefined1 local_61;
  uint local_60 [2];
  char *local_58;
  char *local_54;
  undefined1 local_50;
  uint local_4c;
  int local_48;
  char *local_44;
  char *local_40;
  char acStack_3c [16];
  _func_void_ulong_ulong_void_ptr_ulong_void_ptr *local_2c;
  
  iVar5 = DAT_00020b24 + 0x20530;
  puVar6 = *(undefined4 **)(iVar5 + DAT_00020b28);
  MonCtrl::ConPrintfMessage((char *)*puVar6,DAT_00020b2c + 0x2053c);
  MonCtrl::ConPrintfMessage((char *)*puVar6,DAT_00020b30 + 0x2054e,param_1);
  MonCtrl::ConPrintfMessage((char *)*puVar6,DAT_00020b34 + 0x2055c,param_2);
  MprCtrlLog::SetStartApiLog('\x05',0x347);
  MemUtil::MemSet8(a_Stack_1c4,'\0',0xc4);
  if (param_1 == 0xffffffff) {
    return 0xffffffff;
  }
  piVar8 = *(int **)(iVar5 + DAT_00020b38);
  MWF::ObjLock::Lock((ObjLock *)(*piVar8 + 0x70));
  p_Var9 = (_MediaInfo *)*piVar8;
  iVar2 = _MediaInfo::GetMMgrId(p_Var9,param_1);
  iVar3 = _MediaInfo::GetDsysId(p_Var9,param_1);
  MonCtrl::ConPrintfMessage((char *)*puVar6,DAT_00020b3c + 0x205aa,iVar2);
  MonCtrl::ConPrintfMessage((char *)*puVar6,DAT_00020b40 + 0x205c0,iVar3);
  if (param_2 != 0) {
    if (param_2 == 1) {
      if (iVar3 != 0) {
        uVar7 = 0;
        goto LAB_00020ae8;
      }
      if (iVar2 != 0) {
        p_Var9 = (_MediaInfo *)*piVar8;
        uVar4 = _MediaInfo::GetDeviceType(p_Var9,param_1);
        _MediaInfo::SetDsysId(p_Var9,param_1,uVar4,iVar2);
        uVar7 = 0;
        goto LAB_00020ae8;
      }
      goto LAB_0002061c;
    }
    goto switchD_0002065a_default;
  }
  if (iVar2 != 0) {
    uVar7 = 0;
    goto LAB_00020ae8;
  }
  if (iVar3 != 0) {
    p_Var9 = (_MediaInfo *)*piVar8;
    uVar4 = _MediaInfo::GetDeviceType(p_Var9,param_1);
    _MediaInfo::SetMMgrId(p_Var9,param_1,uVar4,iVar3);
    uVar7 = 0;
    goto LAB_00020ae8;
  }
LAB_0002061c:
  iVar2 = GetMediaInfo(param_1,a_Stack_1c4);
  if (iVar2 != 0) goto switchD_0002065a_default;
  iVar2 = GetCreateMMgrType(a_Stack_1c4);
  MemUtil::MemSet8(acStack_3c,'\0',0x10);
  CreatePrefix(acStack_1c0,acStack_3c);
  uVar7 = 0;
  switch(iVar2) {
  case 0:
    MonCtrl::ConPrintfMessage((char *)*puVar6,DAT_00020b44 + 0x2067c,param_1);
    local_58 = acStack_1c0;
    local_54 = acStack_3c;
    local_50 = 0;
    local_2c = (_func_void_ulong_ulong_void_ptr_ulong_void_ptr *)0x0;
    local_60[1] = 7;
    puVar10 = *(ulong **)(iVar5 + DAT_00020b48);
    local_60[0] = param_1;
    iVar2 = MprIf::NewDvdDcfMMgr((DvdDcfCreateParam *)*puVar10,local_60);
    if (iVar2 == 0) {
      if (param_2 == 1) {
        _MediaInfo::SetDsysId((_MediaInfo *)*piVar8,param_1,7,local_2c);
      }
      else {
        _MediaInfo::SetMMgrId((_MediaInfo *)*piVar8,param_1,7,local_2c);
      }
      MprIf::SetCallbackFunc(*puVar10,local_2c,*(ulong *)(iVar5 + DAT_00020b50),local_2c);
      MprCtrlInputEvent::Init(*(MprCtrlInputEvent **)(iVar5 + DAT_00020b54),(uint)local_2c);
      goto LAB_00020ae8;
    }
    break;
  case 1:
    MonCtrl::ConPrintfMessage((char *)*puVar6,DAT_00020b58 + 0x20728,param_1);
    local_80[1] = 2;
    local_1cc = 2;
    local_74 = acStack_1c0;
    local_80[2] = 1;
    local_70 = acStack_3c;
    local_64 = 0;
    local_6c = 9999;
    local_68 = 9999;
    local_80[0] = param_1;
    local_63 = IsRelayRecSupport();
    local_62 = 1;
    local_61 = IsDpofSupport();
    local_2c = (_func_void_ulong_ulong_void_ptr_ulong_void_ptr *)0x0;
    puVar10 = *(ulong **)(iVar5 + DAT_00020b48);
    iVar2 = MprIf::NewHddAviMMgr((HddAviCreateParam *)*puVar10,local_80);
    goto LAB_00020a80;
  case 2:
    MonCtrl::ConPrintfMessage((char *)*puVar6,DAT_00020b5c + 0x2079c,param_1);
    local_a0[1] = 3;
    if (local_13e == '\0') {
      local_a0[2] = 2;
    }
    else {
      local_a0[2] = 1;
    }
    local_94 = acStack_1c0;
    local_84 = 0;
    local_90 = acStack_3c;
    local_8c = 9999;
    local_88 = 9999;
    local_a0[0] = param_1;
    local_83 = IsRelayRecSupport();
    local_82 = 1;
    local_81 = IsDpofSupport();
    local_2c = (_func_void_ulong_ulong_void_ptr_ulong_void_ptr *)0x0;
    puVar10 = *(ulong **)(iVar5 + DAT_00020b48);
    iVar2 = MprIf::NewMsAviMMgr((MsAviCreateParam *)*puVar10,local_a0);
    if (iVar2 != 0) break;
    if (param_2 == 1) {
      p_Var9 = (_MediaInfo *)*piVar8;
      local_1cc = 3;
      goto LAB_00020aa2;
    }
    p_Var9 = (_MediaInfo *)*piVar8;
    local_1cc = 3;
    goto LAB_00020a92;
  case 3:
  case 7:
    MonCtrl::ConPrintfMessage((char *)*puVar6,DAT_00020b60 + 0x20836,param_1);
    if (iVar2 == 3) {
      local_bc = 6;
    }
    else {
      local_bc = 8;
    }
    local_a4 = 0;
    local_b8 = 1;
    local_b4 = acStack_1c0;
    local_b0 = acStack_3c;
    local_ac = 9999;
    local_a8 = 9999;
    local_c0 = param_1;
    local_a3 = IsRelayRecSupport();
    local_a2 = IsInternalFlashAviSupport();
    local_a1 = IsDpofSupport();
    local_2c = (_func_void_ulong_ulong_void_ptr_ulong_void_ptr *)0x0;
    puVar10 = *(ulong **)(iVar5 + DAT_00020b48);
    iVar2 = MprIf::NewFlashAviMMgr((FlashAviCreateParam *)*puVar10,&local_c0);
    if (iVar2 != 0) break;
    if (param_2 == 1) {
      _MediaInfo::SetDsysId((_MediaInfo *)*piVar8,param_1,6,local_2c);
    }
    else {
      _MediaInfo::SetMMgrId((_MediaInfo *)*piVar8,param_1,6,local_2c);
    }
    MprIf::SetCallbackFunc(*puVar10,local_2c,*(ulong *)(iVar5 + DAT_00020b50),local_2c);
    if (local_a2 == '\0') goto LAB_00020ae8;
    goto LAB_00020ac4;
  case 4:
    MonCtrl::ConPrintfMessage((char *)*puVar6,DAT_00020b64 + 0x20904,param_1);
    local_44 = acStack_1c0;
    local_48 = local_1a8;
    local_4c = param_1;
    if ((local_1a8 == 3) || (local_1a8 == 8)) {
      local_40 = acStack_3c;
      local_2c = (_func_void_ulong_ulong_void_ptr_ulong_void_ptr *)0x0;
      puVar10 = *(ulong **)(iVar5 + DAT_00020b48);
      iVar2 = MprIf::NewBgmMMgr((BgmCreateParam *)*puVar10,&local_4c);
      if (iVar2 == 0) {
        if (param_2 == 1) {
          _MediaInfo::SetDsysId((_MediaInfo *)*piVar8,param_1,local_1a8,local_2c);
        }
        else {
          _MediaInfo::SetMMgrId((_MediaInfo *)*piVar8,param_1,local_1a8,local_2c);
        }
        MprIf::SetCallbackFunc(*puVar10,local_2c,*(ulong *)(iVar5 + DAT_00020b50),local_2c);
        goto LAB_00020ae8;
      }
    }
    break;
  case 5:
    MonCtrl::ConPrintfMessage((char *)*puVar6,DAT_00020b68 + 0x2099e,param_1);
    local_e0[2] = (uint)local_13c;
    local_e0[1] = 4;
    local_d4 = acStack_1c0;
    local_c4 = 0;
    local_d0 = acStack_3c;
    local_1cc = 4;
    local_cc = 9999;
    local_c8 = 9999;
    local_e0[0] = param_1;
    local_c3 = IsRelayRecSupport();
    local_c2 = 1;
    local_c1 = IsDpofSupport();
    local_2c = (_func_void_ulong_ulong_void_ptr_ulong_void_ptr *)0x0;
    puVar10 = *(ulong **)(iVar5 + DAT_00020b48);
    iVar2 = MprIf::NewSsdAviMMgr((SsdAviCreateParam *)*puVar10,local_e0);
    goto LAB_00020a80;
  case 6:
    MonCtrl::ConPrintfMessage((char *)*puVar6,DAT_00020b6c + 0x20a18,param_1);
    local_100[2] = (uint)local_17e;
    local_e4 = 0;
    local_100[1] = 9;
    local_f4 = acStack_1c0;
    local_1cc = 9;
    local_f0 = acStack_3c;
    local_ec = 9999;
    local_e8 = 9999;
    local_100[0] = param_1;
    local_e3 = IsRelayRecSupport();
    local_e2 = 1;
    local_e1 = IsDpofSupport();
    local_2c = (_func_void_ulong_ulong_void_ptr_ulong_void_ptr *)0x0;
    puVar10 = *(ulong **)(iVar5 + DAT_00020b48);
    iVar2 = MprIf::NewUsbAviMMgr((UsbAviCreateParam *)*puVar10,local_100);
LAB_00020a80:
    if (iVar2 == 0) {
      if (param_2 == 1) {
        p_Var9 = (_MediaInfo *)*piVar8;
LAB_00020aa2:
        _MediaInfo::SetDsysId(p_Var9,param_1,local_1cc,local_2c);
      }
      else {
        p_Var9 = (_MediaInfo *)*piVar8;
LAB_00020a92:
        _MediaInfo::SetMMgrId(p_Var9,param_1,local_1cc,local_2c);
      }
      MprIf::SetCallbackFunc(*puVar10,local_2c,*(ulong *)(iVar5 + DAT_00020b50),local_2c);
LAB_00020ac4:
      p_Var1 = local_2c;
      uVar11 = *puVar10;
      GetAviManagedContentTypes();
      MprIf::SetAviManagedContentTypes(uVar11,(ulong)p_Var1);
      goto LAB_00020ae8;
    }
  }
switchD_0002065a_default:
  uVar7 = 0xffffffff;
LAB_00020ae8:
  MWF::ObjLock::Unlock((ObjLock *)(*piVar8 + 0x70));
  if ((MprCtrlUpmEvent *)**(undefined4 **)(iVar5 + DAT_00020b70) != (MprCtrlUpmEvent *)0x0) {
    MprCtrlUpmEvent::UpdateMediaInhInfo((MprCtrlUpmEvent *)**(undefined4 **)(iVar5 + DAT_00020b70));
  }
  MonCtrl::ConPrintfMessage((char *)*puVar6,DAT_00020b74 + 0x20b06);
  MprCtrlLog::SetEndApiLog('\x05',uVar7,0x4cf);
  return uVar7;
}


/* 00020b78 */

/* MprCtrl::CreateMMgr(unsigned int) */

void MprCtrl::CreateMMgr(uint param_1)

{
                    /* WARNING: Could not recover jumptable at 0x0001ed08. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*(code *)PTR_CreateMMgrExec_0004bd74)(param_1,0);
  return;
}


/* 00020b88 */

/* MprCtrl::DeleteMMgrExec(unsigned int, MprCtrl::CreateIfType) */

void MprCtrl::DeleteMMgrExec(uint param_1,int param_2)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  int *piVar4;
  _MediaInfo *p_Var5;
  
  iVar3 = DAT_00020c4c + 0x20b9a;
  MonCtrl::ConPrintfMessage
            ((char *)**(undefined4 **)(iVar3 + DAT_00020c50),DAT_00020c54 + 0x20ba2,param_1);
  MprCtrlLog::SetStartApiLog('\x06',0x4e7);
  if (param_1 == 0xffffffff) {
    return;
  }
  piVar4 = *(int **)(iVar3 + DAT_00020c58);
  MWF::ObjLock::Lock((ObjLock *)(*piVar4 + 0x70));
  if (param_2 == 1) {
    p_Var5 = (_MediaInfo *)*piVar4;
    uVar1 = _MediaInfo::GetDsysId(p_Var5,param_1);
    _MediaInfo::RemoveDsysId(p_Var5,param_1);
    if (uVar1 == 0) goto LAB_0001eaac;
    iVar2 = _MediaInfo::GetMMgrId((_MediaInfo *)*piVar4,param_1);
  }
  else {
    p_Var5 = (_MediaInfo *)*piVar4;
    uVar1 = _MediaInfo::GetMMgrId(p_Var5,param_1);
    _MediaInfo::RemoveMMgrId(p_Var5,param_1);
    if (uVar1 == 0) goto LAB_0001eaac;
    iVar2 = _MediaInfo::GetDsysId((_MediaInfo *)*piVar4,param_1);
  }
  if (iVar2 == 0) {
    MprIf::DeleteMMgr(**(ulong **)(iVar3 + DAT_00020c5c));
    MprCtrlInputEvent::Clear(*(MprCtrlInputEvent **)(iVar3 + DAT_00020c60),uVar1);
  }
LAB_0001eaac:
  MWF::ObjLock::Unlock((ObjLock *)(*piVar4 + 0x70));
  (*(code *)PTR_SetEndApiLog_0004bcb4)(6,0,0x512);
  return;
}


/* 00020c64 */

/* MprCtrl::DeleteMMgr(unsigned int) */

void MprCtrl::DeleteMMgr(uint param_1)

{
                    /* WARNING: Could not recover jumptable at 0x0001f3b0. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*(code *)PTR_DeleteMMgrExec_0004bf90)(param_1,0);
  return;
}


/* 00020c74 */

/* MprCtrl::Destroy() */

void MprCtrl::Destroy(void)

{
  int *piVar1;
  MprIf *pMVar2;
  void *pvVar3;
  char *pcVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int *piVar8;
  undefined4 *puVar9;
  _MediaInfo *this;
  MprCtrlUpmEvent *this_00;
  int *piVar10;
  undefined4 *puVar11;
  undefined4 *puVar12;
  
  iVar6 = DAT_00020e64;
  MprCtrlLog::SetStartApiLog('\x03',0x25a);
  iVar6 = iVar6 + 0x20c8c;
  pcVar4 = *(char **)(iVar6 + DAT_00020e68);
  if (*pcVar4 == '\0') {
    return;
  }
  iVar7 = 0;
  do {
    piVar10 = *(int **)(iVar6 + DAT_00020e6c);
    iVar5 = *piVar10 + iVar7 * 0x10;
    if (*(int *)(iVar5 + 4) != 0) {
      DeleteMMgr(*(uint *)(iVar5 + 8));
    }
    iVar7 = iVar7 + 1;
  } while (iVar7 != 5);
  _MediaInfo::Init((_MediaInfo *)*piVar10);
  puVar12 = *(undefined4 **)(iVar6 + DAT_00020e70);
  _MprEnterInfo::Init((_MprEnterInfo *)*puVar12);
  puVar11 = *(undefined4 **)(iVar6 + DAT_00020e74);
  _RecLineTable::Init((_RecLineTable *)*puVar11);
  piVar8 = *(int **)(iVar6 + DAT_00020e78);
  piVar1 = (int *)*piVar8;
  if (piVar1 != (int *)0x0) {
    (**(code **)(*piVar1 + 4))();
    *piVar8 = 0;
  }
  piVar8 = *(int **)(iVar6 + DAT_00020e7c);
  piVar1 = (int *)*piVar8;
  if (piVar1 != (int *)0x0) {
    (**(code **)(*piVar1 + 4))();
    *piVar8 = 0;
  }
  piVar8 = *(int **)(iVar6 + DAT_00020e80);
  piVar1 = (int *)*piVar8;
  if (piVar1 != (int *)0x0) {
    (**(code **)(*piVar1 + 4))();
    *piVar8 = 0;
  }
  piVar8 = *(int **)(iVar6 + DAT_00020e84);
  piVar1 = (int *)*piVar8;
  if (piVar1 != (int *)0x0) {
    (**(code **)(*piVar1 + 4))();
    *piVar8 = 0;
  }
  piVar8 = *(int **)(iVar6 + DAT_00020e88);
  piVar1 = (int *)*piVar8;
  if (piVar1 != (int *)0x0) {
    (**(code **)(*piVar1 + 4))();
    *piVar8 = 0;
  }
  piVar8 = *(int **)(iVar6 + DAT_00020e8c);
  piVar1 = (int *)*piVar8;
  if (piVar1 != (int *)0x0) {
    (**(code **)(*piVar1 + 4))();
    *piVar8 = 0;
  }
  piVar8 = *(int **)(iVar6 + DAT_00020e90);
  piVar1 = (int *)*piVar8;
  if (piVar1 != (int *)0x0) {
    (**(code **)(*piVar1 + 4))();
    *piVar8 = 0;
  }
  puVar9 = *(undefined4 **)(iVar6 + DAT_00020e94);
  pMVar2 = (MprIf *)*puVar9;
  if (pMVar2 != (MprIf *)0x0) {
    MprIf::Destroy(pMVar2);
    *puVar9 = 0;
  }
  piVar8 = *(int **)(iVar6 + DAT_00020e98);
  piVar1 = (int *)*piVar8;
  if (piVar1 != (int *)0x0) {
    (**(code **)(*piVar1 + 4))();
    *piVar8 = 0;
  }
  piVar8 = *(int **)(iVar6 + DAT_00020e9c);
  piVar1 = (int *)*piVar8;
  if (piVar1 != (int *)0x0) {
    (**(code **)(*piVar1 + 4))();
    *piVar8 = 0;
  }
  piVar8 = *(int **)(iVar6 + DAT_00020ea0);
  piVar1 = (int *)*piVar8;
  if (piVar1 != (int *)0x0) {
    (**(code **)(*piVar1 + 4))();
    *piVar8 = 0;
  }
  piVar8 = *(int **)(iVar6 + DAT_00020ea4);
  piVar1 = (int *)*piVar8;
  if (piVar1 != (int *)0x0) {
    (**(code **)(*piVar1 + 4))();
    *piVar8 = 0;
  }
  this = (_MediaInfo *)*piVar10;
  if (this != (_MediaInfo *)0x0) {
    _MediaInfo::~_MediaInfo(this);
    operator_delete(this);
    *piVar10 = 0;
  }
  if ((void *)*puVar12 != (void *)0x0) {
    operator_delete((void *)*puVar12);
    *puVar12 = 0;
  }
  if ((void *)*puVar11 != (void *)0x0) {
    operator_delete((void *)*puVar11);
    *puVar11 = 0;
  }
  puVar11 = *(undefined4 **)(iVar6 + DAT_00020ea8);
  pvVar3 = (void *)*puVar11;
  if (pvVar3 != (void *)0x0) {
    operator_delete(pvVar3);
    *puVar11 = 0;
  }
  puVar11 = *(undefined4 **)(iVar6 + DAT_00020eac);
  this_00 = (MprCtrlUpmEvent *)*puVar11;
  if (this_00 != (MprCtrlUpmEvent *)0x0) {
    MprCtrlUpmEvent::~MprCtrlUpmEvent(this_00);
    operator_delete(this_00);
    *puVar11 = 0;
  }
  piVar1 = *(int **)(iVar6 + DAT_00020eb0);
  piVar10 = (int *)*piVar1;
  if (piVar10 != (int *)0x0) {
    (**(code **)(*piVar10 + 4))();
    *piVar1 = 0;
  }
  puVar11 = *(undefined4 **)(iVar6 + DAT_00020eb4);
  pvVar3 = (void *)*puVar11;
  if (pvVar3 != (void *)0x0) {
    operator_delete(pvVar3);
    *puVar11 = 0;
  }
  piVar1 = *(int **)(iVar6 + DAT_00020eb8);
  piVar10 = (int *)*piVar1;
  if (piVar10 != (int *)0x0) {
    (**(code **)(*piVar10 + 4))();
    *piVar1 = 0;
  }
  iVar7 = DAT_00020ebc;
  *pcVar4 = '\0';
  **(undefined2 **)(iVar6 + iVar7) = 0xffff;
  **(undefined2 **)(iVar6 + DAT_00020ec0) = 0xffff;
  (*(code *)PTR_SetEndApiLog_0004bcb4)(3,0,0x2e2);
  return;
}


/* 00020ec4 */

/* MprCtrl::GetMMgrId(unsigned int) */

undefined4 MprCtrl::GetMMgrId(uint param_1)

{
  undefined4 uVar1;
  int *piVar2;
  
  piVar2 = *(int **)(DAT_00020efc + 0x20ecc + DAT_00020f00);
  MWF::ObjLock::Lock((ObjLock *)(*piVar2 + 0x70));
  if (param_1 == 0xffffffff) {
    uVar1 = 0;
  }
  else {
    uVar1 = _MediaInfo::GetMMgrId((_MediaInfo *)*piVar2,param_1);
  }
  MWF::ObjLock::Unlock((ObjLock *)(*piVar2 + 0x70));
  return uVar1;
}


/* 00020f04 */

/* MprCtrl::GetDsysId(unsigned int) */

undefined4 MprCtrl::GetDsysId(uint param_1)

{
  undefined4 uVar1;
  int *piVar2;
  
  piVar2 = *(int **)(DAT_00020f3c + 0x20f0c + DAT_00020f40);
  MWF::ObjLock::Lock((ObjLock *)(*piVar2 + 0x70));
  if (param_1 == 0xffffffff) {
    uVar1 = 0;
  }
  else {
    uVar1 = _MediaInfo::GetDsysId((_MediaInfo *)*piVar2,param_1);
  }
  MWF::ObjLock::Unlock((ObjLock *)(*piVar2 + 0x70));
  return uVar1;
}


/* 00020f44 */

/* MprCtrl::GetDeviceType(unsigned int) */

undefined4 MprCtrl::GetDeviceType(uint param_1)

{
  undefined4 uVar1;
  int *piVar2;
  _MediaInfo *this;
  
  piVar2 = *(int **)(DAT_00020f74 + 0x20f4c + DAT_00020f78);
  MWF::ObjLock::Lock((ObjLock *)(*piVar2 + 0x70));
  this = (_MediaInfo *)*piVar2;
  uVar1 = _MediaInfo::GetDeviceType(this,param_1);
  MWF::ObjLock::Unlock((ObjLock *)(this + 0x70));
  return uVar1;
}


/* 00020f7c */

/* MprCtrl::GetMediaId(unsigned int) */

undefined4 MprCtrl::GetMediaId(uint param_1)

{
  undefined4 uVar1;
  int *piVar2;
  
  piVar2 = *(int **)(DAT_00020fb0 + 0x20f84 + DAT_00020fb4);
  MWF::ObjLock::Lock((ObjLock *)(*piVar2 + 0x70));
  if (param_1 == 0) {
    uVar1 = 0xffffffff;
  }
  else {
    uVar1 = _MediaInfo::GetMediaId((_MediaInfo *)*piVar2,param_1);
  }
  MWF::ObjLock::Unlock((ObjLock *)(*piVar2 + 0x70));
  return uVar1;
}


/* 00020fb8 */

/* MprCtrl::GetMediaIdList(unsigned int, unsigned int*, unsigned int*) */

void MprCtrl::GetMediaIdList(uint param_1,uint *param_2,uint *param_3)

{
  int *piVar1;
  
  piVar1 = *(int **)(DAT_00020fec + 0x20fc6 + DAT_00020ff0);
  MWF::ObjLock::Lock((ObjLock *)(*piVar1 + 0x70));
  _MediaInfo::GetMediaIdList((_MediaInfo *)*piVar1,param_1,param_2,param_3);
  (*(code *)PTR_Unlock_0004c134)(*piVar1 + 0x70);
  return;
}


/* 00020ff4 */

/* MprCtrl::AcquireEnter(MprCtrl::EnterType, unsigned int*) */

undefined4 MprCtrl::AcquireEnter(uint param_1,undefined4 *param_2)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 *puVar3;
  
  iVar2 = DAT_00021040 + 0x21004;
  if (param_2 == (undefined4 *)0x0) {
    MonCtrl::ConPutMessage((char *)**(undefined4 **)(iVar2 + DAT_00021044));
    return 0;
  }
  *param_2 = 0;
  puVar3 = *(undefined4 **)(iVar2 + DAT_0002104c);
  MWF::ObjLock::Lock((ObjLock *)*puVar3);
  uVar1 = _MprEnterInfo::Acquire((_MprEnterInfo *)**(undefined4 **)(iVar2 + DAT_00021050),param_1);
  *param_2 = uVar1;
  MWF::ObjLock::Unlock((ObjLock *)*puVar3);
  return 1;
}


/* 00021054 */

/* MprCtrl::ReleaseEnter(MprCtrl::EnterType, unsigned int*) */

bool MprCtrl::ReleaseEnter(uint param_1,undefined4 *param_2)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  bool bVar4;
  _MprEnterInfo *this;
  undefined4 *puVar5;
  
  iVar3 = DAT_000210c8 + 0x21064;
  if (param_2 == (undefined4 *)0x0) {
    MonCtrl::ConPutMessage((char *)**(undefined4 **)(iVar3 + DAT_000210cc));
    bVar4 = false;
  }
  else {
    *param_2 = 0;
    puVar5 = *(undefined4 **)(iVar3 + DAT_000210d4);
    MWF::ObjLock::Lock((ObjLock *)*puVar5);
    this = (_MprEnterInfo *)**(undefined4 **)(iVar3 + DAT_000210d8);
    iVar1 = _MprEnterInfo::Get(this,param_1);
    bVar4 = iVar1 != 0;
    if (bVar4) {
      uVar2 = _MprEnterInfo::Release(this,param_1);
      *param_2 = uVar2;
    }
    else {
      MonCtrl::ConPutMessage((char *)**(undefined4 **)(iVar3 + DAT_000210cc));
    }
    MWF::ObjLock::Unlock((ObjLock *)*puVar5);
  }
  return bVar4;
}


/* 000210e0 */

/* MprCtrl::GetEnterCount(MprCtrl::EnterType, unsigned int*) */

undefined4 MprCtrl::GetEnterCount(uint param_1,undefined4 *param_2)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 *puVar3;
  
  iVar2 = DAT_0002112c + 0x210f0;
  if (param_2 == (undefined4 *)0x0) {
    MonCtrl::ConPutMessage((char *)**(undefined4 **)(iVar2 + DAT_00021130));
    return 0;
  }
  *param_2 = 0;
  puVar3 = *(undefined4 **)(iVar2 + DAT_00021138);
  MWF::ObjLock::Lock((ObjLock *)*puVar3);
  uVar1 = _MprEnterInfo::Get((_MprEnterInfo *)**(undefined4 **)(iVar2 + DAT_0002113c),param_1);
  *param_2 = uVar1;
  MWF::ObjLock::Unlock((ObjLock *)*puVar3);
  return 1;
}


/* 00021140 */

/* MprCtrl::GetRecLine(unsigned int, unsigned int*) */

bool MprCtrl::GetRecLine(uint param_1,uint *param_2)

{
  int iVar1;
  uint uVar2;
  ObjLock *this;
  uint extraout_r3;
  uint uVar3;
  int iVar4;
  undefined4 *puVar5;
  bool bVar6;
  
  iVar1 = DAT_000211c4;
  iVar4 = DAT_000211b8 + 0x21154;
  if ((param_1 == 0xffffffff) || (param_2 == (uint *)0x0)) {
    bVar6 = false;
    MonCtrl::ConPutMessage((char *)**(undefined4 **)(iVar4 + DAT_000211bc));
  }
  else {
    *param_2 = 0;
    puVar5 = *(undefined4 **)(iVar4 + iVar1);
    MWF::ObjLock::Lock((ObjLock *)*puVar5);
    uVar2 = _RecLineTable::GetLine((_RecLineTable *)**(undefined4 **)(iVar4 + DAT_000211c8),param_1)
    ;
    bVar6 = uVar2 != 0xffffffff;
    uVar3 = extraout_r3;
    if (bVar6) {
      uVar3 = uVar2;
    }
    this = (ObjLock *)*puVar5;
    if (!bVar6) {
      uVar3 = *param_2;
    }
    *param_2 = uVar3;
    MWF::ObjLock::Unlock(this);
    MonCtrl::ConPrintfMessage
              ((char *)**(undefined4 **)(iVar4 + DAT_000211cc),DAT_000211d0 + 0x211ac,uVar2);
  }
  return bVar6;
}


/* 000211d4 */

/* MprCtrl::ReleaseRecLine(unsigned int) */

void MprCtrl::ReleaseRecLine(uint param_1)

{
  int iVar1;
  undefined4 *puVar2;
  
  iVar1 = DAT_00021210 + 0x211e4;
  puVar2 = *(undefined4 **)(iVar1 + DAT_00021214);
  MWF::ObjLock::Lock((ObjLock *)*puVar2);
  _RecLineTable::Remove((_RecLineTable *)**(undefined4 **)(iVar1 + DAT_00021218),param_1);
  MWF::ObjLock::Unlock((ObjLock *)*puVar2);
  (*(code *)PTR_ConPrintfMessage_0004c114)
            (**(undefined4 **)(iVar1 + DAT_0002121c),DAT_00021220 + 0x21208,param_1);
  return;
}


/* 00021224 */

/* MprCtrl::GetLine2MediaId(unsigned int, unsigned int*) */

bool MprCtrl::GetLine2MediaId(uint param_1,uint *param_2)

{
  int iVar1;
  uint uVar2;
  ObjLock *this;
  uint extraout_r3;
  uint uVar3;
  int iVar4;
  undefined4 *puVar5;
  bool bVar6;
  
  iVar1 = DAT_000212a0;
  iVar4 = DAT_00021294 + 0x21234;
  if (param_2 == (uint *)0x0) {
    MonCtrl::ConPutMessage((char *)**(undefined4 **)(iVar4 + DAT_00021298));
    bVar6 = false;
  }
  else {
    *param_2 = 0;
    puVar5 = *(undefined4 **)(iVar4 + iVar1);
    MWF::ObjLock::Lock((ObjLock *)*puVar5);
    uVar2 = _RecLineTable::GetMediaId
                      ((_RecLineTable *)**(undefined4 **)(iVar4 + DAT_000212a4),param_1);
    bVar6 = uVar2 != 0xffffffff;
    uVar3 = extraout_r3;
    if (bVar6) {
      uVar3 = uVar2;
    }
    this = (ObjLock *)*puVar5;
    if (!bVar6) {
      uVar3 = *param_2;
    }
    *param_2 = uVar3;
    MWF::ObjLock::Unlock(this);
    MonCtrl::ConPrintfMessage
              ((char *)**(undefined4 **)(iVar4 + DAT_000212a8),DAT_000212ac + 0x2128a,uVar2);
  }
  return bVar6;
}


/* 000212b0 */

/* MprCtrl::SetAriMnfiData(MPR::ContentType, MPR::VQuality, unsigned char*) */

undefined4 MprCtrl::SetAriMnfiData(undefined4 param_1,undefined4 param_2,undefined1 *param_3)

{
  undefined1 uVar1;
  
  if (param_3 != (undefined1 *)0x0) {
    MemUtil::MemSet8(param_3,'\0',0x10);
    switch(param_2) {
    case 0:
      uVar1 = 2;
      break;
    case 1:
      *param_3 = 1;
      return 1;
    case 2:
      uVar1 = 0;
      break;
    case 3:
      uVar1 = 3;
      break;
    case 4:
      uVar1 = 4;
      break;
    case 5:
      uVar1 = 5;
      break;
    case 6:
      uVar1 = 6;
      break;
    case 7:
      uVar1 = 7;
      break;
    case 8:
      uVar1 = 9;
      break;
    case 9:
      uVar1 = 10;
      break;
    default:
      *param_3 = 0xf;
      return 1;
    }
    *param_3 = uVar1;
    return 1;
  }
  MonCtrl::ConPutMessage((char *)**(undefined4 **)(DAT_00021324 + 0x212b8 + DAT_00021328));
  return 0;
}


/* 00021330 */

/* MprCtrl::SetVideoQuality(char*, DefStruct::VQuality*) */

undefined4 MprCtrl::SetVideoQuality(char *param_1,VQuality *param_2)

{
  undefined4 uVar1;
  
  if ((param_1 != (char *)0x0) && (param_2 != (VQuality *)0x0)) {
    switch(*param_1) {
    case '\0':
      uVar1 = 2;
      break;
    case '\x01':
      *(undefined4 *)param_2 = 1;
      return 1;
    case '\x02':
      uVar1 = 0;
      break;
    case '\x03':
      uVar1 = 3;
      break;
    case '\x04':
      uVar1 = 4;
      break;
    case '\x05':
      uVar1 = 5;
      break;
    case '\x06':
      uVar1 = 6;
      break;
    case '\a':
      uVar1 = 7;
      break;
    default:
      *(undefined4 *)param_2 = 0xff;
      return 1;
    case '\t':
      uVar1 = 8;
      break;
    case '\n':
      uVar1 = 9;
    }
    *(undefined4 *)param_2 = uVar1;
    return 1;
  }
  MonCtrl::ConPutMessage((char *)**(undefined4 **)(DAT_0002139c + 0x2133a + DAT_000213a0));
  return 0;
}


/* 000213a8 */

/* MprCtrl::GetStillSizeTable() */

void MprCtrl::GetStillSizeTable(void)

{
  (*(code *)PTR_GetStillSizeTable_0004c13c)
            (**(undefined4 **)(DAT_000213c0 + 0x213b0 + DAT_000213c4));
  return;
}


/* 000213c8 */

/* MprCtrl::GetStillSize(unsigned short, unsigned short, DefStruct::StillSize*) */

void MprCtrl::GetStillSize(ushort param_1,ushort param_2,StillSize *param_3)

{
                    /* WARNING: Could not recover jumptable at 0x0001edc4. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*(code *)PTR_GetStillSize_0004bdb0)
            (**(undefined4 **)(DAT_000213e8 + 0x213d8 + DAT_000213ec),param_1,param_2,param_3);
  return;
}


/* 000213f0 */

/* MprCtrl::GetStillRecInfo(DefStruct::StillSizeInfo*, int*, int*) */

void MprCtrl::GetStillRecInfo(StillSizeInfo *param_1,int *param_2,int *param_3)

{
  uint local_1c [2];
  
  local_1c[0] = 0;
  MprCtrlStillMgr::GetStillRecInfo
            ((MprCtrlStillMgr *)**(undefined4 **)(DAT_00021424 + 0x2140c + DAT_00021428),param_1,
             param_2,param_3,local_1c);
  return;
}


/* 0002142c */

/* MprCtrl::GetStillRecInfo(DefStruct::StillSizeInfo*, int*, int*, unsigned int*) */

void MprCtrl::GetStillRecInfo(StillSizeInfo *param_1,int *param_2,int *param_3,uint *param_4)

{
  MprCtrlStillMgr::GetStillRecInfo
            ((MprCtrlStillMgr *)**(undefined4 **)(DAT_00021458 + 0x2143a + DAT_0002145c),param_1,
             param_2,param_3,param_4);
  return;
}


/* 00021460 */

/* MprCtrl::GetStillDataInfo(int, int, int, int, int, int, MprCtrlStill::StillDataInfo*) */

void MprCtrl::GetStillDataInfo
               (int param_1,int param_2,int param_3,int param_4,int param_5,int param_6,
               StillDataInfo *param_7)

{
  MprCtrlStillMgr::GetStillDataInfo
            ((MprCtrlStillMgr *)**(undefined4 **)(DAT_00021498 + 0x2146e + DAT_0002149c),param_1,
             param_2,param_3,param_4,param_5,param_6,param_7);
  return;
}


/* 000214a0 */

/* MprCtrl::GetDualRecCaptureCount() */

undefined4 MprCtrl::GetDualRecCaptureCount(void)

{
  uint uVar1;
  undefined4 *puVar2;
  undefined4 uVar3;
  
  puVar2 = *(undefined4 **)(DAT_000214dc + 0x214ac + DAT_000214e0);
  MonCtrl::ConPrintfMessage((char *)*puVar2,DAT_000214e4 + 0x214b2);
  uVar1 = GetDualRecType();
  if (uVar1 < 2) {
    uVar3 = *(undefined4 *)(DAT_000214e8 + 0x214c6 + uVar1 * 4);
  }
  else {
    uVar3 = 3;
  }
  MonCtrl::ConPrintfMessage((char *)*puVar2,DAT_000214ec + 0x214d6,uVar3);
  return uVar3;
}


/* 000214f0 */

/* MprCtrl::GetModelVersion(unsigned short*, unsigned short*) */

undefined4 MprCtrl::GetModelVersion(ushort *param_1,ushort *param_2)

{
  ObjLock *this;
  int iVar1;
  undefined4 *puVar2;
  
  iVar1 = DAT_00021528 + 0x21502;
  puVar2 = *(undefined4 **)(iVar1 + DAT_0002152c);
  MWF::ObjLock::Lock((ObjLock *)*puVar2);
  this = (ObjLock *)*puVar2;
  *param_1 = **(ushort **)(iVar1 + DAT_00021530);
  *param_2 = **(ushort **)(iVar1 + DAT_00021534);
  MWF::ObjLock::Unlock(this);
  return 0;
}


/* 00021538 */

/* MprCtrl::SetModelVersion() */

undefined4 MprCtrl::SetModelVersion(void)

{
  undefined4 *puVar1;
  int iVar2;
  char *pcVar3;
  int iVar4;
  int iVar5;
  undefined4 uVar6;
  undefined4 *puVar7;
  undefined1 auStack_30 [4];
  int local_2c;
  undefined4 *local_20;
  int local_1c;
  
  local_1c = 0;
  local_20 = (undefined4 *)0x0;
  iVar2 = osal_dynamic_id(0x2a,199,&local_1c);
  iVar4 = local_1c;
  iVar5 = DAT_00021698 + 0x21558;
  if (iVar2 == 0) {
    memset(auStack_30,0,0x10);
    iVar2 = FUN_0001ffd4(DAT_0002168c,0x11d,iVar4,auStack_30,iVar4);
    if ((iVar2 == 0) && (iVar2 = local_2c, local_2c == 0)) {
      iVar2 = osal_valloc_msg_wait(DAT_00021690,&local_20,0xc,1);
      puVar1 = local_20;
      if (iVar2 == 0) {
        MemUtil::MemSet8(local_20,'\0',0xc);
        *puVar1 = 5;
        FUN_0001ffb4(local_20,local_1c);
        iVar2 = osal_snd_sync_msg(DAT_00021690,local_20);
        if (iVar2 == 0) {
          puVar7 = *(undefined4 **)(iVar5 + DAT_000216b0);
          MWF::ObjLock::Lock((ObjLock *)*puVar7);
          iVar4 = DAT_000216b8;
          **(undefined2 **)(iVar5 + DAT_000216b4) = *(undefined2 *)((int)puVar1 + 6);
          **(undefined2 **)(iVar5 + iVar4) = *(undefined2 *)(puVar1 + 2);
          MonCtrl::ConPrintf((char *)**(undefined4 **)(iVar5 + DAT_000216bc),DAT_000216c0 + 0x2161c)
          ;
          MWF::ObjLock::Unlock((ObjLock *)*puVar7);
          uVar6 = 0;
          goto LAB_00021624;
        }
        iVar4 = DAT_000216ac + 0x215f0;
        pcVar3 = (char *)**(undefined4 **)(iVar5 + DAT_0002169c);
      }
      else {
        iVar4 = DAT_000216a8 + 0x215ba;
        pcVar3 = (char *)**(undefined4 **)(iVar5 + DAT_0002169c);
      }
    }
    else {
      iVar4 = DAT_000216a4 + 0x21594;
      pcVar3 = (char *)**(undefined4 **)(iVar5 + DAT_0002169c);
    }
  }
  else {
    iVar4 = DAT_000216a0 + 0x21564;
    pcVar3 = (char *)**(undefined4 **)(iVar5 + DAT_0002169c);
  }
  MonCtrl::ConPrintf(pcVar3,iVar4,iVar2);
  uVar6 = 0xffffffff;
LAB_00021624:
  if ((local_20 != (undefined4 *)0x0) && (iVar4 = osal_free_msg(DAT_00021690), iVar4 != 0)) {
    MonCtrl::ConPrintf((char *)**(undefined4 **)(iVar5 + DAT_0002169c),DAT_000216c4 + 0x2163c,iVar4)
    ;
  }
  iVar4 = local_1c;
  if (local_1c != 0) {
    memset(auStack_30,0,0x10);
    iVar4 = FUN_0001ffd4(DAT_00021694,0x11d,iVar4,auStack_30,iVar4);
    if ((iVar4 != 0) || (iVar4 = local_2c, local_2c != 0)) {
      MonCtrl::ConPrintf((char *)**(undefined4 **)(iVar5 + DAT_0002169c),DAT_000216c8 + 0x21670,
                         iVar4);
    }
    osal_dynamic_id(0x4a,0,local_1c);
  }
  return uVar6;
}


/* 000216cc */

/* MprCtrl::GetFixedArea(MprCtrl::FixedAreaType, void**, unsigned int*) */

void MprCtrl::GetFixedArea(int param_1,undefined4 *param_2,undefined4 *param_3)

{
  undefined4 *puVar1;
  undefined4 uVar2;
  
  if (param_1 == 0) {
    puVar1 = *(undefined4 **)(DAT_000216ec + 0x216d4 + DAT_000216f0);
    uVar2 = puVar1[1];
    *param_2 = *puVar1;
  }
  else {
    uVar2 = 0;
    *param_2 = 0;
  }
  *param_3 = uVar2;
  return;
}


/* 000216f4 */

/* MprCtrl::SetFixedArea(unsigned int, unsigned int) */

void MprCtrl::SetFixedArea(uint param_1,uint param_2)

{
  int *piVar1;
  
  piVar1 = *(int **)(DAT_00021710 + 0x21700 + DAT_00021714);
  *piVar1 = param_1 + 0x5c000;
  piVar1[1] = 0x8000;
  return;
}


/* 00021718 */

/* MprCtrl::Init() */

void MprCtrl::Init(void)

{
  bool bVar1;
  char *pcVar2;
  undefined4 uVar3;
  _MediaInfo *this;
  _MprEnterInfo *this_00;
  _RecLineTable *this_01;
  void *pvVar4;
  MprCtrlStillMgr *pMVar5;
  ObjLock *this_02;
  RsrcMgr *pRVar6;
  int iVar7;
  EventHandlerWrapper *this_03;
  EventSender *this_04;
  EventReceiver *this_05;
  EventSwitcher *this_06;
  ulong uVar8;
  uint uVar9;
  StillSizeInfo *pSVar10;
  undefined4 uVar11;
  int iVar12;
  MprCtrlUpmEvent *this_07;
  ushort uVar13;
  int *piVar14;
  int *piVar15;
  uint uVar16;
  int iVar17;
  int *piVar18;
  undefined4 *puVar19;
  ulong *puVar20;
  undefined4 *puVar21;
  undefined4 *puVar22;
  uint uVar23;
  undefined4 *puVar24;
  undefined4 *puVar25;
  undefined4 *puVar26;
  int *piVar27;
  undefined1 auStack_7bc [1836];
  undefined4 local_90;
  undefined4 uStack_8c;
  undefined4 uStack_88;
  undefined4 uStack_84;
  undefined4 local_80;
  undefined4 uStack_7c;
  undefined4 uStack_78;
  undefined4 uStack_74;
  undefined4 local_70;
  undefined4 uStack_6c;
  undefined4 uStack_68;
  undefined4 uStack_64;
  char *local_60;
  int local_5c;
  undefined4 local_58;
  undefined1 *local_54;
  undefined4 local_50;
  undefined1 local_4c;
  undefined4 local_44;
  undefined4 local_40;
  undefined4 local_3c;
  undefined4 local_38;
  undefined1 auStack_34 [8];
  MprIf *local_2c [2];
  
  iVar17 = DAT_00021cb8;
  MprCtrlLog::SetStartApiLog('\x02',0x86);
  iVar17 = iVar17 + 0x21738;
  if (**(char **)(iVar17 + DAT_00021cbc) != '\0') {
    return;
  }
  **(char **)(iVar17 + DAT_00021cbc) = '\x01';
  MprCtrlMcmd::Init();
  pcVar2 = (char *)MprCtrlMcmd::GetMonMsg();
  **(undefined4 **)(iVar17 + DAT_00021cc0) = pcVar2;
  MonCtrl::ConPutMessage(pcVar2);
  uVar3 = MprCtrlMcmd::GetMonErr();
  puVar19 = *(undefined4 **)(iVar17 + DAT_00021cc8);
  *puVar19 = uVar3;
  uVar3 = MprCtrlMcmd::GetMonDbg();
  **(undefined4 **)(iVar17 + DAT_00021ccc) = uVar3;
  this = operator_new(0x8c);
  _MediaInfo::_MediaInfo(this);
  piVar27 = *(int **)(iVar17 + DAT_00021cd0);
  *piVar27 = (int)this;
  this_00 = operator_new(0x2c);
  _MprEnterInfo::_MprEnterInfo(this_00);
  **(undefined4 **)(iVar17 + DAT_00021cd4) = this_00;
  this_01 = operator_new(0xc);
  _RecLineTable::_RecLineTable(this_01);
  **(undefined4 **)(iVar17 + DAT_00021cd8) = this_01;
  pvVar4 = operator_new__(0x14);
  puVar20 = *(ulong **)(iVar17 + DAT_00021cdc);
  *puVar20 = (ulong)pvVar4;
  MprCtrlCnv::Init();
  pMVar5 = operator_new(0x1c);
  MprCtrlStillMgr::MprCtrlStillMgr(pMVar5);
  puVar21 = *(undefined4 **)(iVar17 + DAT_00021ce0);
  *puVar21 = pMVar5;
  MprCtrlStillMgr::GetBackupStillSize(pMVar5);
  MprCtrlStillMgr::CreateStillData((MprCtrlStillMgr *)*puVar21);
  piVar14 = *(int **)(iVar17 + DAT_00021ce4);
  if (*piVar14 == 0) {
    this_02 = operator_new(0x1c);
    MWF::ObjLock::ObjLock(this_02);
    *piVar14 = (int)this_02;
  }
  bVar1 = (bool)IsStillCacheSupport();
  DmmAccess::Init(bVar1);
  pRVar6 = operator_new(0x24);
  MWF::RsrcMgr::RsrcMgr(pRVar6,0x19,1);
  **(undefined4 **)(iVar17 + DAT_00021ce8) = pRVar6;
  iVar7 = IsMultiRecSupport();
  puVar22 = *(undefined4 **)(iVar17 + DAT_00021cec);
  puVar24 = *(undefined4 **)(iVar17 + DAT_00021cf0);
  puVar25 = *(undefined4 **)(iVar17 + DAT_00021cf4);
  puVar26 = *(undefined4 **)(iVar17 + DAT_00021cf8);
  if (iVar7 == 0) {
    pRVar6 = operator_new(0x24);
    MWF::RsrcMgr::RsrcMgr(pRVar6,0x1d,1);
    *puVar22 = pRVar6;
    pRVar6 = operator_new(0x24);
    MWF::RsrcMgr::RsrcMgr(pRVar6,0x1e,1);
    *puVar24 = pRVar6;
    pRVar6 = operator_new(0x24);
    MWF::RsrcMgr::RsrcMgr(pRVar6,0x1f,1);
    *puVar25 = pRVar6;
    pRVar6 = operator_new(0x24);
    MWF::RsrcMgr::RsrcMgr(pRVar6,0xbe,1);
  }
  else {
    pRVar6 = operator_new(0x24);
    MWF::RsrcMgr::RsrcMgr(pRVar6,0x1d,6);
    *puVar22 = pRVar6;
    pRVar6 = operator_new(0x24);
    MWF::RsrcMgr::RsrcMgr(pRVar6,0x1e,3);
    *puVar24 = pRVar6;
    pRVar6 = operator_new(0x24);
    MWF::RsrcMgr::RsrcMgr(pRVar6,0x1f,3);
    *puVar25 = pRVar6;
    pRVar6 = operator_new(0x24);
    MWF::RsrcMgr::RsrcMgr(pRVar6,0xbe,3);
  }
  *puVar26 = pRVar6;
  pRVar6 = operator_new(0x24);
  MWF::RsrcMgr::RsrcMgr(pRVar6,0x35,1);
  **(undefined4 **)(iVar17 + DAT_00021cfc) = pRVar6;
  pRVar6 = operator_new(0x24);
  MWF::RsrcMgr::RsrcMgr(pRVar6,0x33,1);
  **(undefined4 **)(iVar17 + DAT_00021d00) = pRVar6;
  pRVar6 = operator_new(0x24);
  MWF::RsrcMgr::RsrcMgr(pRVar6,0x34,1);
  **(undefined4 **)(iVar17 + DAT_00021d04) = pRVar6;
  piVar14 = *(int **)(iVar17 + DAT_00021d08);
  if (((*piVar14 == 0) && (piVar18 = *(int **)(iVar17 + DAT_00021d0c), *piVar18 == 0)) &&
     (piVar15 = *(int **)(iVar17 + DAT_00021d10), *piVar15 == 0)) {
    this_03 = operator_new(0x48);
    EventHandlerWrapper::EventHandlerWrapper(this_03);
    *piVar15 = (int)this_03;
    this_04 = operator_new(0xc);
    MWF::EventSender::EventSender(this_04);
    *piVar14 = (int)this_04;
    this_05 = operator_new(0x38);
    MWF::EventReceiver::EventReceiver(this_05);
    *piVar18 = (int)this_05;
    MWF::EventReceiver::GenerateEventId((uint)this_05);
    MWF::EventReceiver::SetEventHandler((EventHandler *)*piVar18);
    MWF::EventSender::SetEventReceiver((EventReceiver *)*piVar14);
  }
  piVar14 = *(int **)(iVar17 + DAT_00021d14);
  if (*piVar14 == 0) {
    this_06 = operator_new(0x14);
    EventSwitcher::EventSwitcher(this_06);
    iVar7 = DAT_00021d18;
    *piVar14 = (int)this_06;
    local_90 = *(undefined4 *)(iVar7 + 0x219b6);
    uStack_8c = *(undefined4 *)(iVar7 + 0x219ba);
    uStack_88 = *(undefined4 *)(iVar7 + 0x219be);
    uStack_84 = *(undefined4 *)(iVar7 + 0x219c2);
    local_80 = *(undefined4 *)(iVar7 + 0x219c6);
    uStack_7c = *(undefined4 *)(iVar7 + 0x219ca);
    uStack_78 = *(undefined4 *)(iVar7 + 0x219ce);
    uStack_74 = *(undefined4 *)(iVar7 + 0x219d2);
    local_70 = *(undefined4 *)(iVar7 + 0x219d6);
    uStack_6c = *(undefined4 *)(iVar7 + 0x219da);
    uStack_68 = *(undefined4 *)(iVar7 + 0x219de);
    uStack_64 = *(undefined4 *)(iVar7 + 0x219e2);
    EventSwitcher::AddInstance(this_06,this_06);
    EventSwitcher::AddCallbackFunc
              ((EventSwitcher *)*piVar14,(EventSwitcher *)*piVar14,3,(_CallbackEntry *)&local_90);
  }
  piVar14 = *(int **)(iVar17 + DAT_00021d1c);
  if (*piVar14 == 0) {
    uVar8 = GetSupportContentTypes();
    MprIf::SetCreateParam_SupportContentTypes(uVar8);
    uVar8 = GetSupportMedia();
    MprIf::SetCreateParam_SupportMedia(uVar8);
    bVar1 = (bool)IsGpsSupport();
    MprIf::SetCreateParam_GpsParam(bVar1);
    bVar1 = (bool)IsMultiRecSupport();
    MprIf::SetCreateParam_MultiMovieRec(bVar1);
    bVar1 = (bool)IsTcUbSupport();
    MprIf::SetCreateParam_RecTcUbParam(bVar1);
    MprIf::SetCreateParam_RecCamInfoParam(true);
    iVar7 = IsSerialNumberRecSupport();
    if (iVar7 == 0) {
      uVar8 = 0xffffffff;
    }
    else {
      uVar9 = GetSerialNumber();
      iVar7 = 1;
      uVar23 = 0;
      uVar16 = 0x18;
      do {
        uVar8 = uVar16;
        uVar23 = iVar7 * (uVar9 >> (uVar8 & 0xff) & 0xff) + uVar23;
        iVar7 = iVar7 << 8;
        uVar16 = uVar8 - 8;
      } while (uVar8 - 8 != 0xfffffff8);
      iVar7 = 1;
      uVar16 = uVar8;
      do {
        uVar9 = uVar16 & 0xff;
        uVar16 = uVar16 + 4;
        uVar8 = iVar7 * (uVar23 >> uVar9 & 0xf) + uVar8;
        iVar7 = iVar7 * 10;
      } while (uVar16 != 0x20);
    }
    MprIf::SetCreateParam_SerialNumber(uVar8);
    pMVar5 = (MprCtrlStillMgr *)*puVar21;
    pSVar10 = (StillSizeInfo *)MprCtrlStillMgr::GetStillDataTable(pMVar5);
    uVar8 = MprCtrlStillMgr::GetStillDataTableNum(pMVar5);
    MprIf::SetCreateParam_StillSizeInfo(pSVar10,uVar8);
    uVar3 = MprCtrlStillMgr::GetDualRecStillMode();
    uVar11 = GetDualRecCaptureCount();
    puVar21 = operator_new(0x48);
    memset(puVar21,0,0x48);
    puVar22 = *(undefined4 **)(iVar17 + DAT_00021d20);
    puVar21[2] = uVar11;
    puVar21[3] = uVar3;
    *puVar22 = puVar21;
    *puVar21 = uVar3;
    puVar21[1] = 1;
    puVar21[4] = 1;
    puVar21[7] = 1;
    puVar21[10] = 1;
    puVar21[0xd] = 1;
    puVar21[0x10] = 1;
    puVar21[5] = uVar11;
    puVar21[6] = uVar3;
    puVar21[8] = uVar11;
    puVar21[9] = uVar3;
    puVar21[0xb] = uVar11;
    puVar21[0xc] = uVar3;
    puVar21[0xe] = uVar11;
    puVar21[0xf] = uVar3;
    MprIf::SetCreateParam_dualRecStillInfo(6,puVar21);
    memcpy(auStack_7bc,(void *)(DAT_00021d24 + 0x21af8),0x72c);
    MemUtil::MemSet8(&local_90,'\0',0x11);
    iVar7 = GetModelName((char *)&local_90);
    local_60 = (char *)&local_90;
    if (iVar7 < 0) {
      local_60 = (char *)(DAT_00021d28 + 0x21b14);
    }
    local_5c = DAT_00021d2c + 0x21b24;
    local_58 = GetTvSystem();
    local_54 = auStack_7bc;
    local_50 = 0x99;
    local_4c = 0x2f;
    local_44 = Backup_read_4Byte(DAT_00021cb0);
    local_40 = Backup_read_4Byte(DAT_00021cb4);
    local_3c = 0;
    local_38 = 0;
    uVar23 = Backup_read_4Byte(DAT_00021cb0);
    uVar16 = Backup_read_4Byte(DAT_00021cb4);
    SetFixedArea(uVar23,uVar16);
    local_2c[0] = (MprIf *)0x0;
    iVar7 = MprIf::Create((CreateParam *)&local_60,local_2c,false);
    if (iVar7 != 0) {
      *piVar14 = 0;
      uVar23 = 8;
      uVar13 = 0x21d;
      goto LAB_00021c5c;
    }
    *piVar14 = (int)local_2c[0];
    MprIf::Init();
    MprIf::SetCallbackFunc
              ((_func_void_ulong_ulong_void_ptr_ulong_void_ptr *)*piVar14,
               *(ulong *)(iVar17 + DAT_00021d30),
               (_func_void_ulong_ulong_void_ptr_ulong_void_ptr *)*piVar14);
    iVar7 = MprIf::GetPreFirstMountInfo((PreFirstMountInfo *)*piVar14,*puVar20);
    if (iVar7 == 0) {
      MWF::ObjMsg::ObjMsg(auStack_34,0,0);
      iVar7 = EventHandlerWrapper::WaitEvent(**(uint **)(iVar17 + DAT_00021d10));
      if (iVar7 == 0) {
        MWF::EventReceiver::RecvEvent((ObjMsg *)**(undefined4 **)(iVar17 + DAT_00021d0c));
      }
      MWF::ObjMsg::~ObjMsg(auStack_34);
    }
  }
  iVar7 = 0;
  do {
    uVar23 = *(uint *)(*piVar27 + iVar7 * 0x10 + 8);
    if ((uVar23 != 0xffffffff) && (iVar12 = CreateMMgr(uVar23), iVar12 != 0)) {
      MonCtrl::ConPrintf((char *)*puVar19,DAT_00021d34 + 0x21c26,
                         *(undefined4 *)(*piVar27 + iVar7 * 0x10 + 8),iVar12);
    }
    iVar7 = iVar7 + 1;
  } while (iVar7 != 5);
  this_07 = operator_new(0x44);
  MprCtrlUpmEvent::MprCtrlUpmEvent(this_07);
  **(undefined4 **)(iVar17 + DAT_00021d38) = this_07;
  iVar17 = SetModelVersion();
  if (iVar17 != 0) {
    MonCtrl::ConPrintf((char *)*puVar19,DAT_00021d3c + 0x21c52,iVar17);
  }
  uVar23 = 0;
  uVar13 = 0x245;
LAB_00021c5c:
  MprCtrlLog::SetEndApiLog('\x02',uVar23,uVar13);
  return;
}


/* 00021d40 */

void _INIT_1(void)

{
  int iVar1;
  MprCtrlInputEvent *this;
  
  iVar1 = DAT_00021d64 + 0x21d4c;
  this = *(MprCtrlInputEvent **)(iVar1 + DAT_00021d68);
  MprCtrlInputEvent::MprCtrlInputEvent(this);
  (*(code *)PTR___aeabi_atexit_0004c184)
            (this,*(undefined4 *)(iVar1 + DAT_00021d6c),*(undefined4 *)(iVar1 + DAT_00021d70));
  return;
}


/* 00021d74 */

/* MprCtrl::GetTvSystem() */

undefined4 MprCtrl::GetTvSystem(void)

{
  int iVar1;
  int iVar2;
  byte local_19 [5];
  
  local_19[0] = 0;
  iVar1 = BackupLib::GetEepData(DAT_00021dc8,'\x01',local_19);
  iVar2 = DAT_00021dcc + 0x21d92;
  if (iVar1 < 0) {
    SetSelfCheckLog(true);
    MonCtrl::ConPrintfMessage
              ((char *)**(undefined4 **)(iVar2 + DAT_00021dd0),DAT_00021dd4 + 0x21da6,iVar1);
  }
  else if (local_19[0] < 2) {
    return *(undefined4 *)(DAT_00021dd8 + 0x21db8 + (uint)local_19[0] * 4);
  }
  return 0;
}


/* 00021ddc */

/* MprCtrl::GetSupportContentTypes() */

uint MprCtrl::GetSupportContentTypes(void)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  char local_19 [5];
  
  local_19[0] = '\0';
  iVar1 = BackupLib::GetEepData(DAT_00021f1c,'\x01',local_19);
  iVar3 = DAT_00021f34 + 0x21dfa;
  if (iVar1 < 0) {
    SetSelfCheckLog(true);
    uVar2 = 1;
    MonCtrl::ConPrintfMessage
              ((char *)**(undefined4 **)(iVar3 + DAT_00021f38),DAT_00021f3c + 0x21e10,iVar1);
  }
  else if (local_19[0] == '\x01') {
    uVar2 = 9;
  }
  else {
    uVar2 = 1;
  }
  iVar1 = BackupLib::GetEepData(DAT_00021f20,'\x01',local_19);
  if (iVar1 < 0) {
    SetSelfCheckLog(true);
    MonCtrl::ConPrintfMessage
              ((char *)**(undefined4 **)(iVar3 + DAT_00021f38),DAT_00021f40 + 0x21e40,iVar1);
  }
  else if (local_19[0] == '\x01') {
    uVar2 = uVar2 | 0x10;
  }
  iVar1 = BackupLib::GetEepData(DAT_00021f24,'\x01',local_19);
  if (iVar1 < 0) {
    SetSelfCheckLog(true);
    MonCtrl::ConPrintfMessage
              ((char *)**(undefined4 **)(iVar3 + DAT_00021f38),DAT_00021f44 + 0x21e70,iVar1);
  }
  else if (local_19[0] == '\x01') {
    uVar2 = uVar2 | 4;
  }
  iVar1 = BackupLib::GetEepData(DAT_00021f28,'\x01',local_19);
  if (iVar1 < 0) {
    SetSelfCheckLog(true);
    MonCtrl::ConPrintfMessage
              ((char *)**(undefined4 **)(iVar3 + DAT_00021f38),DAT_00021f48 + 0x21ea0,iVar1);
  }
  else if (local_19[0] == '\x01') {
    uVar2 = uVar2 | 0x100;
  }
  iVar1 = BackupLib::GetEepData(DAT_00021f2c,'\x01',local_19);
  if (iVar1 < 0) {
    SetSelfCheckLog(true);
    MonCtrl::ConPrintfMessage
              ((char *)**(undefined4 **)(iVar3 + DAT_00021f38),DAT_00021f4c + 0x21ed0,iVar1);
  }
  else if (local_19[0] == '\x01') {
    uVar2 = uVar2 | 0x200;
  }
  iVar1 = BackupLib::GetEepData(DAT_00021f30,'\x01',local_19);
  if (iVar1 < 0) {
    SetSelfCheckLog(true);
    MonCtrl::ConPrintfMessage
              ((char *)**(undefined4 **)(iVar3 + DAT_00021f38),DAT_00021f50 + 0x21f00,iVar1);
  }
  else if (local_19[0] == '\x01') {
    uVar2 = uVar2 | 0x80;
  }
  return uVar2;
}


/* 00021f54 */

/* MprCtrl::GetSupportMedia() */

undefined4 MprCtrl::GetSupportMedia(void)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  byte local_11;
  
  local_11 = 0;
  iVar1 = BackupLib::GetEepData(DAT_00021fac,'\x01',&local_11);
  iVar3 = DAT_00021fb0 + 0x21f72;
  if (iVar1 < 0) {
    SetSelfCheckLog(true);
    MonCtrl::ConPrintfMessage
              ((char *)**(undefined4 **)(iVar3 + DAT_00021fb4),DAT_00021fb8 + 0x21f86,iVar1);
  }
  else {
    uVar2 = local_11 - 1 & 0xff;
    if (uVar2 < 4) {
      return *(undefined4 *)(DAT_00021fbc + 0x21f9c + uVar2 * 4);
    }
  }
  return 4;
}


/* 00021fc0 */

/* MprCtrl::GetAviManagedContentTypes() */

uint MprCtrl::GetAviManagedContentTypes(void)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  undefined4 *puVar4;
  char local_19;
  
  local_19 = '\0';
  iVar3 = DAT_00022108 + 0x21fda;
  puVar4 = *(undefined4 **)(iVar3 + DAT_00022110);
  MonCtrl::ConPrintfMessage((char *)*puVar4,DAT_0002210c + 0x21fde);
  iVar1 = BackupLib::GetEepData(DAT_000220f4,'\x01',&local_19);
  if (iVar1 < 0) {
    SetSelfCheckLog(true);
    uVar2 = 1;
    MonCtrl::ConPrintfMessage
              ((char *)**(undefined4 **)(iVar3 + DAT_00022114),DAT_00022118 + 0x22006,iVar1);
  }
  else if (local_19 == '\x01') {
    uVar2 = 9;
  }
  else {
    uVar2 = 1;
  }
  iVar1 = BackupLib::GetEepData(DAT_000220f8,'\x01',&local_19);
  if (iVar1 < 0) {
    SetSelfCheckLog(true);
    MonCtrl::ConPrintfMessage((char *)*puVar4,DAT_0002211c + 0x22036,iVar1);
  }
  else if (local_19 == '\x01') {
    uVar2 = uVar2 | 0x10;
  }
  iVar1 = BackupLib::GetEepData(DAT_000220fc,'\x01',&local_19);
  if (iVar1 < 0) {
    SetSelfCheckLog(true);
    MonCtrl::ConPrintfMessage
              ((char *)**(undefined4 **)(iVar3 + DAT_00022114),DAT_00022120 + 0x22066,iVar1);
  }
  else if (local_19 == '\x01') {
    uVar2 = uVar2 | 4;
  }
  iVar1 = BackupLib::GetEepData(DAT_00022100,'\x01',&local_19);
  if (iVar1 < 0) {
    SetSelfCheckLog(true);
    MonCtrl::ConPrintfMessage
              ((char *)**(undefined4 **)(iVar3 + DAT_00022114),DAT_00022124 + 0x22098,iVar1);
  }
  else if (local_19 == '\x01') {
    uVar2 = uVar2 | 0x100;
  }
  iVar1 = BackupLib::GetEepData(DAT_00022104,'\x01',&local_19);
  if (iVar1 < 0) {
    SetSelfCheckLog(true);
    MonCtrl::ConPrintfMessage
              ((char *)**(undefined4 **)(iVar3 + DAT_00022114),DAT_00022128 + 0x220ca,iVar1);
  }
  else if (local_19 == '\x01') {
    uVar2 = uVar2 | 0x200;
  }
  MonCtrl::ConPrintfMessage((char *)*puVar4,DAT_0002212c + 0x220e4,uVar2);
  return uVar2;
}


/* 00022130 */

/* MprCtrl::IsGpsSupport() */

bool MprCtrl::IsGpsSupport(void)

{
  char cVar1;
  int iVar2;
  int iVar3;
  char local_19 [5];
  
  local_19[0] = '\0';
  iVar2 = BackupLib::GetEepData(DAT_00022180,'\x01',local_19);
  cVar1 = local_19[0];
  iVar3 = DAT_00022184 + 0x2214e;
  if (-1 >= iVar2) {
    SetSelfCheckLog(true);
    MonCtrl::ConPrintfMessage
              ((char *)**(undefined4 **)(iVar3 + DAT_00022188),DAT_0002218c + 0x22162,iVar2);
  }
  return -1 < iVar2 && cVar1 == '\x01';
}


/* 00022190 */

/* MprCtrl::IsMultiRecSupport() */

bool MprCtrl::IsMultiRecSupport(void)

{
  char cVar1;
  int iVar2;
  int iVar3;
  char local_19 [5];
  
  local_19[0] = '\0';
  iVar2 = BackupLib::GetEepData(DAT_000221e0,'\x01',local_19);
  cVar1 = local_19[0];
  iVar3 = DAT_000221e4 + 0x221ae;
  if (-1 >= iVar2) {
    SetSelfCheckLog(true);
    MonCtrl::ConPrintfMessage
              ((char *)**(undefined4 **)(iVar3 + DAT_000221e8),DAT_000221ec + 0x221c2,iVar2);
  }
  return -1 < iVar2 && cVar1 == '\x01';
}


/* 000221f0 */

/* MprCtrl::IsCaptureIdTable() */

bool MprCtrl::IsCaptureIdTable(void)

{
  char cVar1;
  int iVar2;
  int iVar3;
  char local_19 [5];
  
  local_19[0] = '\0';
  iVar2 = BackupLib::GetEepData(DAT_00022240,'\x01',local_19);
  cVar1 = local_19[0];
  iVar3 = DAT_00022244 + 0x2220e;
  if (-1 >= iVar2) {
    SetSelfCheckLog(true);
    MonCtrl::ConPrintfMessage
              ((char *)**(undefined4 **)(iVar3 + DAT_00022248),DAT_0002224c + 0x22222,iVar2);
  }
  return -1 < iVar2 && cVar1 == '\x01';
}


/* 00022250 */

/* MprCtrl::IsDualRecOver18Mbps() */

bool MprCtrl::IsDualRecOver18Mbps(void)

{
  char cVar1;
  int iVar2;
  int iVar3;
  char local_19 [5];
  
  local_19[0] = '\0';
  iVar2 = BackupLib::GetEepData(DAT_000222a0,'\x01',local_19);
  cVar1 = local_19[0];
  iVar3 = DAT_000222a4 + 0x2226e;
  if (-1 >= iVar2) {
    SetSelfCheckLog(true);
    MonCtrl::ConPrintfMessage
              ((char *)**(undefined4 **)(iVar3 + DAT_000222a8),DAT_000222ac + 0x22282,iVar2);
  }
  return -1 < iVar2 && cVar1 == '\x01';
}


/* 000222b0 */

/* MprCtrl::GetSystemColor(MprCtrl::SystemColor, unsigned char*) */

int MprCtrl::GetSystemColor(undefined4 param_1,undefined1 *param_2)

{
  uint uVar1;
  int iVar2;
  ushort uVar3;
  int iVar4;
  undefined4 *puVar5;
  ushort local_1a;
  
  iVar4 = DAT_00022378 + 0x222c0;
  local_1a = 0;
  puVar5 = *(undefined4 **)(iVar4 + DAT_0002237c);
  MonCtrl::ConPrintfMessage((char *)*puVar5,DAT_00022380 + 0x222d4);
  switch(param_1) {
  case 0:
    uVar1 = 0x290000;
    break;
  case 1:
    uVar1 = DAT_00022374;
    break;
  case 2:
    uVar1 = DAT_00022358;
    break;
  case 3:
    uVar1 = DAT_0002235c;
    break;
  case 4:
    uVar1 = DAT_00022360;
    break;
  case 5:
    uVar1 = DAT_00022364;
    break;
  case 6:
    uVar1 = DAT_00022368;
    break;
  case 7:
    uVar1 = DAT_0002236c;
    break;
  case 8:
    uVar1 = DAT_00022370;
    break;
  default:
    return -1;
  }
  iVar2 = BackupLib::GetEepData(uVar1,'\x02',&local_1a);
  uVar3 = local_1a;
  if (iVar2 < 0) {
    SetSelfCheckLog(true);
    MonCtrl::ConPrintfMessage
              ((char *)**(undefined4 **)(iVar4 + DAT_00022384),DAT_00022388 + 0x2232a,iVar2);
    uVar3 = 0;
  }
  iVar4 = DAT_0002238c;
  *param_2 = (char)uVar3;
  MonCtrl::ConPrintfMessage((char *)*puVar5,iVar4 + 0x2233c,(uint)local_1a);
  return iVar2;
}


/* 00022390 */

/* MprCtrl::GetModelName(char*) */

int MprCtrl::GetModelName(char *param_1)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  undefined4 *puVar4;
  
  iVar3 = DAT_000223fc + 0x2239e;
  if (param_1 == (char *)0x0) {
    iVar2 = -100;
  }
  else {
    uVar1 = BackupLib::GetDataSize(DAT_000223f8);
    puVar4 = *(undefined4 **)(iVar3 + DAT_00022400);
    MonCtrl::ConPrintfMessage((char *)*puVar4,DAT_00022404 + 0x223b0,uVar1);
    iVar2 = BackupLib::GetEepData(DAT_000223f8,(uchar)uVar1,param_1);
    if (iVar2 < 0) {
      SetSelfCheckLog(true);
      MonCtrl::ConPrintfMessage
                ((char *)**(undefined4 **)(iVar3 + DAT_00022408),DAT_0002240c + 0x223da,iVar2);
    }
    MonCtrl::ConPrintfMessage((char *)*puVar4,DAT_00022410 + 0x223ea,param_1);
  }
  return iVar2;
}


/* 00022414 */

/* MprCtrl::GetMaxDpofRegistContentNum() */

undefined4 MprCtrl::GetMaxDpofRegistContentNum(void)

{
  int iVar1;
  int iVar2;
  undefined4 *puVar3;
  undefined4 local_1c [2];
  
  local_1c[0] = 0;
  iVar2 = DAT_00022474 + 0x2242c;
  puVar3 = *(undefined4 **)(iVar2 + DAT_0002247c);
  MonCtrl::ConPrintfMessage((char *)*puVar3,DAT_00022478 + 0x22430);
  iVar1 = BackupLib::GetEepData(DAT_00022470,'\x02',local_1c);
  if (iVar1 < 0) {
    SetSelfCheckLog(true);
    MonCtrl::ConPrintfMessage
              ((char *)**(undefined4 **)(iVar2 + DAT_00022480),DAT_00022484 + 0x22456,iVar1);
  }
  MonCtrl::ConPrintfMessage((char *)*puVar3,DAT_00022488 + 0x22462,local_1c[0]);
  return local_1c[0];
}


/* 0002248c */

/* MprCtrl::GetMaxSelectContentNumOnEdit() */

undefined4 MprCtrl::GetMaxSelectContentNumOnEdit(void)

{
  int iVar1;
  int iVar2;
  undefined4 *puVar3;
  undefined4 local_1c [2];
  
  local_1c[0] = 0;
  iVar2 = DAT_000224ec + 0x224a4;
  puVar3 = *(undefined4 **)(iVar2 + DAT_000224f4);
  MonCtrl::ConPrintfMessage((char *)*puVar3,DAT_000224f0 + 0x224a8);
  iVar1 = BackupLib::GetEepData(DAT_000224e8,'\x02',local_1c);
  if (iVar1 < 0) {
    SetSelfCheckLog(true);
    MonCtrl::ConPrintfMessage
              ((char *)**(undefined4 **)(iVar2 + DAT_000224f8),DAT_000224fc + 0x224ce,iVar1);
  }
  MonCtrl::ConPrintfMessage((char *)*puVar3,DAT_00022500 + 0x224da,local_1c[0]);
  return local_1c[0];
}


/* 00022504 */

/* MprCtrl::GetMaxSelectContentNumOnDubbing() */

undefined4 MprCtrl::GetMaxSelectContentNumOnDubbing(void)

{
  int iVar1;
  int iVar2;
  undefined4 *puVar3;
  undefined4 local_1c [2];
  
  local_1c[0] = 0;
  iVar2 = DAT_00022564 + 0x2251c;
  puVar3 = *(undefined4 **)(iVar2 + DAT_0002256c);
  MonCtrl::ConPrintfMessage((char *)*puVar3,DAT_00022568 + 0x22520);
  iVar1 = BackupLib::GetEepData(DAT_00022560,'\x02',local_1c);
  if (iVar1 < 0) {
    SetSelfCheckLog(true);
    MonCtrl::ConPrintfMessage
              ((char *)**(undefined4 **)(iVar2 + DAT_00022570),DAT_00022574 + 0x22546,iVar1);
  }
  MonCtrl::ConPrintfMessage((char *)*puVar3,DAT_00022578 + 0x22552,local_1c[0]);
  return local_1c[0];
}


/* 0002257c */

/* MprCtrl::GetDualRecType() */

undefined4 MprCtrl::GetDualRecType(void)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 *puVar4;
  char local_19 [5];
  
  local_19[0] = '\0';
  iVar2 = DAT_000225ec + 0x22594;
  puVar4 = *(undefined4 **)(iVar2 + DAT_000225f4);
  MonCtrl::ConPrintfMessage((char *)*puVar4,DAT_000225f0 + 0x22598);
  iVar1 = BackupLib::GetEepData(DAT_000225e8,'\x01',local_19);
  if (iVar1 < 0) {
    SetSelfCheckLog(true);
    uVar3 = 1;
    MonCtrl::ConPrintfMessage
              ((char *)**(undefined4 **)(iVar2 + DAT_000225f8),DAT_000225fc + 0x225be,iVar1);
  }
  else if (local_19[0] == '\0') {
    uVar3 = 0;
  }
  else {
    uVar3 = 1;
  }
  MonCtrl::ConPrintfMessage((char *)*puVar4,DAT_00022600 + 0x225da,uVar3);
  return uVar3;
}


/* 00022604 */

/* MprCtrl::IsDpofSupport() */

bool MprCtrl::IsDpofSupport(void)

{
  char cVar1;
  int iVar2;
  int iVar3;
  char local_19 [5];
  
  local_19[0] = '\0';
  iVar2 = BackupLib::GetEepData(DAT_00022654,'\x01',local_19);
  cVar1 = local_19[0];
  iVar3 = DAT_00022658 + 0x22622;
  if (-1 >= iVar2) {
    SetSelfCheckLog(true);
    MonCtrl::ConPrintfMessage
              ((char *)**(undefined4 **)(iVar3 + DAT_0002265c),DAT_00022660 + 0x22636,iVar2);
  }
  return -1 < iVar2 && cVar1 == '\x01';
}


/* 00022664 */

/* MprCtrl::GetColorSpaceInfo(char*) */

int MprCtrl::GetColorSpaceInfo(char *param_1)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = DAT_000226bc + 0x22670;
  if (param_1 == (char *)0x0) {
    iVar2 = -100;
  }
  else {
    uVar1 = BackupLib::GetDataSize(DAT_000226b8);
    MonCtrl::ConPrintfMessage
              ((char *)**(undefined4 **)(iVar3 + DAT_000226c0),DAT_000226c4 + 0x22680,uVar1);
    iVar2 = BackupLib::GetEepData(DAT_000226b8,(uchar)uVar1,param_1);
    if (iVar2 < 0) {
      SetSelfCheckLog(true);
      MonCtrl::ConPrintfMessage
                ((char *)**(undefined4 **)(iVar3 + DAT_000226c8),DAT_000226cc + 0x226a8,iVar2);
    }
  }
  return iVar2;
}


/* 000226d0 */

/* MprCtrl::GetRecLimitTime() */

byte MprCtrl::GetRecLimitTime(void)

{
  int iVar1;
  int iVar2;
  undefined4 *puVar3;
  byte local_19 [5];
  
  local_19[0] = 3;
  iVar2 = DAT_00022730 + 0x226e8;
  puVar3 = *(undefined4 **)(iVar2 + DAT_00022738);
  MonCtrl::ConPrintfMessage((char *)*puVar3,DAT_00022734 + 0x226ec);
  iVar1 = BackupLib::GetEepData(DAT_0002272c,'\x01',local_19);
  if (iVar1 < 0) {
    SetSelfCheckLog(true);
    MonCtrl::ConPrintfMessage
              ((char *)**(undefined4 **)(iVar2 + DAT_0002273c),DAT_00022740 + 0x22712,iVar1);
  }
  MonCtrl::ConPrintfMessage((char *)*puVar3,DAT_00022744 + 0x2271e,(uint)local_19[0]);
  return local_19[0];
}


/* 00022748 */

/* MprCtrl::IsInternalFlashAviSupport() */

bool MprCtrl::IsInternalFlashAviSupport(void)

{
  char cVar1;
  int iVar2;
  int iVar3;
  char local_19 [5];
  
  local_19[0] = '\0';
  iVar2 = BackupLib::GetEepData(DAT_00022798,'\x01',local_19);
  cVar1 = local_19[0];
  iVar3 = DAT_0002279c + 0x22766;
  if (-1 >= iVar2) {
    SetSelfCheckLog(true);
    MonCtrl::ConPrintfMessage
              ((char *)**(undefined4 **)(iVar3 + DAT_000227a0),DAT_000227a4 + 0x2277a,iVar2);
  }
  return -1 < iVar2 && cVar1 == '\x01';
}


/* 000227a8 */

/* MprCtrl::IsSerialNumberRecSupport() */

bool MprCtrl::IsSerialNumberRecSupport(void)

{
  char cVar1;
  int iVar2;
  int iVar3;
  char local_19 [5];
  
  local_19[0] = '\0';
  iVar2 = BackupLib::GetEepData(DAT_000227f8,'\x01',local_19);
  cVar1 = local_19[0];
  iVar3 = DAT_000227fc + 0x227c6;
  if (-1 >= iVar2) {
    SetSelfCheckLog(true);
    MonCtrl::ConPrintfMessage
              ((char *)**(undefined4 **)(iVar3 + DAT_00022800),DAT_00022804 + 0x227da,iVar2);
  }
  return -1 < iVar2 && cVar1 == '\x01';
}


/* 00022808 */

/* MprCtrl::GetSerialNumber() */

undefined4 MprCtrl::GetSerialNumber(void)

{
  int iVar1;
  int iVar2;
  undefined4 local_14;
  
  local_14 = 0;
  iVar1 = BackupLib::GetEepData(DAT_00022848,'\x04',&local_14);
  iVar2 = DAT_0002284c + 0x22826;
  if (iVar1 < 0) {
    SetSelfCheckLog(true);
    MonCtrl::ConPrintfMessage
              ((char *)**(undefined4 **)(iVar2 + DAT_00022850),DAT_00022854 + 0x2283a,iVar1);
  }
  return local_14;
}


/* 00022858 */

/* MprCtrl::IsTcUbSupport() */

bool MprCtrl::IsTcUbSupport(void)

{
  char cVar1;
  int iVar2;
  int iVar3;
  char local_19 [5];
  
  local_19[0] = '\0';
  iVar2 = BackupLib::GetEepData(DAT_000228a8,'\x01',local_19);
  cVar1 = local_19[0];
  iVar3 = DAT_000228ac + 0x22876;
  if (-1 >= iVar2) {
    SetSelfCheckLog(true);
    MonCtrl::ConPrintfMessage
              ((char *)**(undefined4 **)(iVar3 + DAT_000228b0),DAT_000228b4 + 0x2288a,iVar2);
  }
  return -1 < iVar2 && cVar1 == '\x01';
}


/* 000228b8 */

/* MprCtrl::IsYmdDateFormat() */

int MprCtrl::IsYmdDateFormat(void)

{
  int iVar1;
  int iVar2;
  byte local_19 [5];
  
  local_19[0] = 0;
  iVar1 = BackupLib::GetEepData(DAT_00022904,'\x01',local_19);
  iVar2 = DAT_00022908 + 0x228d6;
  if (iVar1 < 0) {
    SetSelfCheckLog(true);
    MonCtrl::ConPrintfMessage
              ((char *)**(undefined4 **)(iVar2 + DAT_0002290c),DAT_00022910 + 0x228ea,iVar1);
    iVar1 = 0;
  }
  else {
    iVar1 = 1 - (uint)local_19[0];
    if (1 < local_19[0]) {
      iVar1 = 0;
    }
  }
  return iVar1;
}


/* 00022914 */

/* MprCtrl::IsStillRawDevelopmentSupport() */

bool MprCtrl::IsStillRawDevelopmentSupport(void)

{
  char cVar1;
  int iVar2;
  int iVar3;
  char local_19 [5];
  
  local_19[0] = '\0';
  iVar2 = BackupLib::GetEepData(DAT_00022964,'\x01',local_19);
  cVar1 = local_19[0];
  iVar3 = DAT_00022968 + 0x22932;
  if (-1 >= iVar2) {
    SetSelfCheckLog(true);
    MonCtrl::ConPrintfMessage
              ((char *)**(undefined4 **)(iVar3 + DAT_0002296c),DAT_00022970 + 0x22946,iVar2);
  }
  return -1 < iVar2 && cVar1 == '\x01';
}


/* 00022974 */

/* MprCtrl::GetRamMapType() */

byte MprCtrl::GetRamMapType(void)

{
  int iVar1;
  int iVar2;
  undefined4 *puVar3;
  byte local_19 [5];
  
  local_19[0] = 0;
  iVar2 = DAT_000229d4 + 0x2298c;
  puVar3 = *(undefined4 **)(iVar2 + DAT_000229dc);
  MonCtrl::ConPrintfMessage((char *)*puVar3,DAT_000229d8 + 0x22990);
  iVar1 = BackupLib::GetEepData(DAT_000229d0,'\x01',local_19);
  if (iVar1 < 0) {
    SetSelfCheckLog(true);
    MonCtrl::ConPrintfMessage
              ((char *)**(undefined4 **)(iVar2 + DAT_000229e0),DAT_000229e4 + 0x229b6,iVar1);
  }
  MonCtrl::ConPrintfMessage((char *)*puVar3,DAT_000229e8 + 0x229c2,(uint)local_19[0]);
  return local_19[0];
}


/* 000229ec */

/* MprCtrl::IsStillCacheSupport() */

bool MprCtrl::IsStillCacheSupport(void)

{
  char cVar1;
  int iVar2;
  int iVar3;
  char local_19 [5];
  
  local_19[0] = '\0';
  iVar2 = BackupLib::GetEepData(DAT_00022a3c,'\x01',local_19);
  cVar1 = local_19[0];
  iVar3 = DAT_00022a40 + 0x22a0a;
  if (-1 >= iVar2) {
    SetSelfCheckLog(true);
    MonCtrl::ConPrintfMessage
              ((char *)**(undefined4 **)(iVar3 + DAT_00022a44),DAT_00022a48 + 0x22a1e,iVar2);
  }
  return -1 < iVar2 && cVar1 == '\x01';
}


/* 00022a4c */

/* MprCtrl::IsStillPlayOnMemorySupport() */

bool MprCtrl::IsStillPlayOnMemorySupport(void)

{
  char cVar1;
  int iVar2;
  int iVar3;
  char local_19 [5];
  
  local_19[0] = '\0';
  iVar2 = BackupLib::GetEepData(DAT_00022a9c,'\x01',local_19);
  cVar1 = local_19[0];
  iVar3 = DAT_00022aa0 + 0x22a6a;
  if (-1 >= iVar2) {
    SetSelfCheckLog(true);
    MonCtrl::ConPrintfMessage
              ((char *)**(undefined4 **)(iVar3 + DAT_00022aa4),DAT_00022aa8 + 0x22a7e,iVar2);
  }
  return -1 < iVar2 && cVar1 == '\x01';
}


/* 00022aac */

/* MprCtrl::IsOledPanel() */

bool MprCtrl::IsOledPanel(void)

{
  char cVar1;
  int iVar2;
  int iVar3;
  char local_19 [5];
  
  local_19[0] = '\0';
  iVar2 = BackupLib::GetEepData(DAT_00022afc,'\x01',local_19);
  cVar1 = local_19[0];
  iVar3 = DAT_00022b00 + 0x22aca;
  if (-1 >= iVar2) {
    SetSelfCheckLog(true);
    MonCtrl::ConPrintfMessage
              ((char *)**(undefined4 **)(iVar3 + DAT_00022b04),DAT_00022b08 + 0x22ade,iVar2);
  }
  return -1 < iVar2 && cVar1 == '\x01';
}


/* 00022b0c */

/* MprCtrl::IsZoomContentsChangeSupport() */

bool MprCtrl::IsZoomContentsChangeSupport(void)

{
  char cVar1;
  int iVar2;
  int iVar3;
  char local_19 [5];
  
  local_19[0] = '\0';
  iVar2 = BackupLib::GetEepData(DAT_00022b5c,'\x01',local_19);
  cVar1 = local_19[0];
  iVar3 = DAT_00022b60 + 0x22b2a;
  if (-1 >= iVar2) {
    SetSelfCheckLog(true);
    MonCtrl::ConPrintfMessage
              ((char *)**(undefined4 **)(iVar3 + DAT_00022b64),DAT_00022b68 + 0x22b3e,iVar2);
  }
  return -1 < iVar2 && cVar1 == '\x01';
}


/* 00022b6c */

/* MprCtrl::IsSoftwareTagSupport() */

bool MprCtrl::IsSoftwareTagSupport(void)

{
  char cVar1;
  int iVar2;
  int iVar3;
  char local_19 [5];
  
  local_19[0] = '\0';
  iVar2 = BackupLib::GetEepData(DAT_00022bbc,'\x01',local_19);
  cVar1 = local_19[0];
  iVar3 = DAT_00022bc0 + 0x22b8a;
  if (-1 >= iVar2) {
    SetSelfCheckLog(true);
    MonCtrl::ConPrintfMessage
              ((char *)**(undefined4 **)(iVar3 + DAT_00022bc4),DAT_00022bc8 + 0x22b9e,iVar2);
  }
  return -1 < iVar2 && cVar1 == '\x01';
}


/* 00022bcc */

/* MprCtrl::IsNetworkWriteTestMode() */

bool MprCtrl::IsNetworkWriteTestMode(void)

{
  char cVar1;
  int iVar2;
  int iVar3;
  char local_19 [5];
  
  local_19[0] = '\0';
  iVar2 = BackupLib::GetEepData(DAT_00022c1c,'\x01',local_19);
  cVar1 = local_19[0];
  iVar3 = DAT_00022c20 + 0x22bea;
  if (-1 >= iVar2) {
    SetSelfCheckLog(true);
    MonCtrl::ConPrintfMessage
              ((char *)**(undefined4 **)(iVar3 + DAT_00022c24),DAT_00022c28 + 0x22bfe,iVar2);
  }
  return -1 < iVar2 && cVar1 == '\x01';
}


/* 00022c2c */

/* MprCtrl::GetDualRecMovieMaxBitrate() */

byte MprCtrl::GetDualRecMovieMaxBitrate(void)

{
  int iVar1;
  int iVar2;
  undefined4 *puVar3;
  byte local_19 [5];
  
  local_19[0] = 0;
  iVar2 = DAT_00022c8c + 0x22c44;
  puVar3 = *(undefined4 **)(iVar2 + DAT_00022c94);
  MonCtrl::ConPrintfMessage((char *)*puVar3,DAT_00022c90 + 0x22c48);
  iVar1 = BackupLib::GetEepData(DAT_00022c88,'\x01',local_19);
  if (iVar1 < 0) {
    SetSelfCheckLog(true);
    MonCtrl::ConPrintfMessage
              ((char *)**(undefined4 **)(iVar2 + DAT_00022c98),DAT_00022c9c + 0x22c6e,iVar1);
  }
  MonCtrl::ConPrintfMessage((char *)*puVar3,DAT_00022ca0 + 0x22c7a,(uint)local_19[0]);
  return local_19[0];
}


/* 00022ca4 */

/* MprCtrl::IsDvMode() */

bool MprCtrl::IsDvMode(void)

{
  char cVar1;
  int iVar2;
  int iVar3;
  char local_19 [5];
  
  local_19[0] = '\0';
  iVar2 = BackupLib::GetEepData(DAT_00022cf4,'\x01',local_19);
  cVar1 = local_19[0];
  iVar3 = DAT_00022cf8 + 0x22cc2;
  if (-1 >= iVar2) {
    SetSelfCheckLog(true);
    MonCtrl::ConPrintfMessage
              ((char *)**(undefined4 **)(iVar3 + DAT_00022cfc),DAT_00022d00 + 0x22cd6,iVar2);
  }
  return -1 < iVar2 && cVar1 == '\a';
}


/* 00022d04 */

/* MprCtrl::GetStillCacheReleaseType() */

byte MprCtrl::GetStillCacheReleaseType(void)

{
  int iVar1;
  int iVar2;
  undefined4 *puVar3;
  byte local_19 [5];
  
  local_19[0] = 0;
  iVar2 = DAT_00022d64 + 0x22d1c;
  puVar3 = *(undefined4 **)(iVar2 + DAT_00022d6c);
  MonCtrl::ConPrintfMessage((char *)*puVar3,DAT_00022d68 + 0x22d20);
  iVar1 = BackupLib::GetEepData(DAT_00022d60,'\x01',local_19);
  if (iVar1 < 0) {
    SetSelfCheckLog(true);
    MonCtrl::ConPrintfMessage
              ((char *)**(undefined4 **)(iVar2 + DAT_00022d70),DAT_00022d74 + 0x22d46,iVar1);
  }
  MonCtrl::ConPrintfMessage((char *)*puVar3,DAT_00022d78 + 0x22d52,(uint)local_19[0]);
  return local_19[0];
}


/* 00022d7c */

/* MprCtrl::IsRelayRecSupport() */

bool MprCtrl::IsRelayRecSupport(void)

{
  char cVar1;
  int iVar2;
  int iVar3;
  char local_19 [5];
  
  local_19[0] = '\0';
  iVar2 = BackupLib::GetEepData(DAT_00022dcc,'\x01',local_19);
  cVar1 = local_19[0];
  iVar3 = DAT_00022dd0 + 0x22d9a;
  if (-1 >= iVar2) {
    SetSelfCheckLog(true);
    MonCtrl::ConPrintfMessage
              ((char *)**(undefined4 **)(iVar3 + DAT_00022dd4),DAT_00022dd8 + 0x22dae,iVar2);
  }
  return -1 < iVar2 && cVar1 == '\x01';
}


/* 00022ddc */

/* MprCtrl::Get4kPlaybackRestrictionType() */

byte MprCtrl::Get4kPlaybackRestrictionType(void)

{
  int iVar1;
  int iVar2;
  undefined4 *puVar3;
  byte local_19 [5];
  
  local_19[0] = 0;
  iVar2 = DAT_00022e3c + 0x22df4;
  puVar3 = *(undefined4 **)(iVar2 + DAT_00022e44);
  MonCtrl::ConPrintfMessage((char *)*puVar3,DAT_00022e40 + 0x22df8);
  iVar1 = BackupLib::GetEepData(DAT_00022e38,'\x01',local_19);
  if (iVar1 < 0) {
    SetSelfCheckLog(true);
    MonCtrl::ConPrintfMessage
              ((char *)**(undefined4 **)(iVar2 + DAT_00022e48),DAT_00022e4c + 0x22e1e,iVar1);
  }
  MonCtrl::ConPrintfMessage((char *)*puVar3,DAT_00022e50 + 0x22e2a,(uint)local_19[0]);
  return local_19[0];
}


/* 00022e54 */

/* MprCtrl::Get4KStillHdmiWaitTime() */

ushort MprCtrl::Get4KStillHdmiWaitTime(void)

{
  int iVar1;
  int iVar2;
  undefined4 *puVar3;
  ushort local_1a [3];
  
  local_1a[0] = 0x96;
  iVar2 = DAT_00022eb4 + 0x22e6c;
  puVar3 = *(undefined4 **)(iVar2 + DAT_00022ebc);
  MonCtrl::ConPrintfMessage((char *)*puVar3,DAT_00022eb8 + 0x22e70);
  iVar1 = BackupLib::GetEepData(DAT_00022eb0,'\x02',local_1a);
  if (iVar1 < 0) {
    SetSelfCheckLog(true);
    MonCtrl::ConPrintfMessage
              ((char *)**(undefined4 **)(iVar2 + DAT_00022ec0),DAT_00022ec4 + 0x22e96,iVar1);
  }
  MonCtrl::ConPrintfMessage((char *)*puVar3,DAT_00022ec8 + 0x22ea2,(uint)local_1a[0]);
  return local_1a[0];
}


/* 00022ecc */

/* MprCtrl::GetMonFltFlagObjImporter(bool*, bool*, bool*) */

void MprCtrl::GetMonFltFlagObjImporter(bool *param_1,bool *param_2,bool *param_3)

{
  int iVar1;
  int iVar2;
  undefined4 *puVar3;
  byte local_21;
  
  local_21 = 0;
  iVar2 = DAT_00022f64 + 0x22ee6;
  puVar3 = *(undefined4 **)(iVar2 + DAT_00022f68);
  MonCtrl::ConPrintfMessage((char *)*puVar3,DAT_00022f6c + 0x22ef4);
  iVar1 = BackupLib::GetEepData(DAT_00022f60,'\x01',&local_21);
  if (iVar1 < 0) {
    SetSelfCheckLog(true);
    MonCtrl::ConPrintfMessage
              ((char *)**(undefined4 **)(iVar2 + DAT_00022f70),DAT_00022f74 + 0x22f1c,iVar1);
    local_21 = 1;
  }
  MonCtrl::ConPrintfMessage((char *)*puVar3,DAT_00022f78 + 0x22f2e,(uint)local_21);
  if (param_1 != (bool *)0x0) {
    *param_1 = (bool)(local_21 & 1);
  }
  if (param_2 != (bool *)0x0) {
    *param_2 = SUB41(((uint)local_21 << 0x1e) >> 0x1f,0);
  }
  if (param_3 != (bool *)0x0) {
    *param_3 = SUB41(((uint)local_21 << 0x1d) >> 0x1f,0);
  }
  return;
}


/* 00022f7c */

/* MprCtrl::GetMonFlt(unsigned int) */

undefined1 MprCtrl::GetMonFlt(uint param_1)

{
  uint uVar1;
  int iVar2;
  undefined1 local_9;
  
  local_9 = 0;
  uVar1 = DAT_00023020;
  if (param_1 != 0x38) {
    if (param_1 < 0x39) {
      uVar1 = DAT_00023030;
      if (param_1 != 0x30) {
        if (param_1 < 0x31) {
          uVar1 = DAT_00023044;
          if ((param_1 != 0x2e) && (uVar1 = DAT_00023050, param_1 != 0x2f)) {
            return 0;
          }
        }
        else {
          uVar1 = DAT_00023038;
          if (((param_1 != 0x34) && (uVar1 = DAT_00023054, param_1 != 0x37)) &&
             (uVar1 = DAT_00023048, param_1 != 0x32)) {
            return 0;
          }
        }
      }
    }
    else {
      uVar1 = DAT_00023028;
      if (param_1 != 0xae) {
        if (param_1 < 0xaf) {
          uVar1 = DAT_00023034;
          if (((param_1 != 0x3a) && (uVar1 = DAT_0002303c, 0x39 < param_1)) &&
             (uVar1 = DAT_0002304c, param_1 != 0xad)) {
            return 0;
          }
        }
        else {
          uVar1 = DAT_00023040;
          if (((param_1 != 0xdd) && (uVar1 = DAT_0002302c, param_1 != 0xf8)) &&
             (uVar1 = DAT_00023024, param_1 != 199)) {
            return 0;
          }
        }
      }
    }
  }
  iVar2 = BackupLib::GetEepData(uVar1,'\x01',&local_9);
  if (iVar2 < 0) {
    SetSelfCheckLog(true);
  }
  return local_9;
}


/* 00023058 */

/* MprCtrl::GetMediaTransferRateXAVC() */

byte MprCtrl::GetMediaTransferRateXAVC(void)

{
  int iVar1;
  int iVar2;
  undefined4 *puVar3;
  byte local_19 [5];
  
  local_19[0] = 0;
  iVar2 = DAT_000230b8 + 0x23070;
  puVar3 = *(undefined4 **)(iVar2 + DAT_000230c0);
  MonCtrl::ConPrintfMessage((char *)*puVar3,DAT_000230bc + 0x23074);
  iVar1 = BackupLib::GetEepData(DAT_000230b4,'\x01',local_19);
  if (iVar1 < 0) {
    SetSelfCheckLog(true);
    MonCtrl::ConPrintfMessage
              ((char *)**(undefined4 **)(iVar2 + DAT_000230c4),DAT_000230c8 + 0x2309a,iVar1);
  }
  MonCtrl::ConPrintfMessage((char *)*puVar3,DAT_000230cc + 0x230a6,(uint)local_19[0]);
  return local_19[0];
}


/* 000230d0 */

/* MprCtrl::GetMediaTransferRateDV() */

byte MprCtrl::GetMediaTransferRateDV(void)

{
  int iVar1;
  int iVar2;
  undefined4 *puVar3;
  byte local_19 [5];
  
  local_19[0] = 0;
  iVar2 = DAT_00023130 + 0x230e8;
  puVar3 = *(undefined4 **)(iVar2 + DAT_00023138);
  MonCtrl::ConPrintfMessage((char *)*puVar3,DAT_00023134 + 0x230ec);
  iVar1 = BackupLib::GetEepData(DAT_0002312c,'\x01',local_19);
  if (iVar1 < 0) {
    SetSelfCheckLog(true);
    MonCtrl::ConPrintfMessage
              ((char *)**(undefined4 **)(iVar2 + DAT_0002313c),DAT_00023140 + 0x23112,iVar1);
  }
  MonCtrl::ConPrintfMessage((char *)*puVar3,DAT_00023144 + 0x2311e,(uint)local_19[0]);
  return local_19[0];
}


/* 00023148 */

/* MprCtrl::GetMediaTransferRateMultiRec() */

byte MprCtrl::GetMediaTransferRateMultiRec(void)

{
  int iVar1;
  int iVar2;
  undefined4 *puVar3;
  byte local_19 [5];
  
  local_19[0] = 0;
  iVar2 = DAT_000231a8 + 0x23160;
  puVar3 = *(undefined4 **)(iVar2 + DAT_000231b0);
  MonCtrl::ConPrintfMessage((char *)*puVar3,DAT_000231ac + 0x23164);
  iVar1 = BackupLib::GetEepData(DAT_000231a4,'\x01',local_19);
  if (iVar1 < 0) {
    SetSelfCheckLog(true);
    MonCtrl::ConPrintfMessage
              ((char *)**(undefined4 **)(iVar2 + DAT_000231b4),DAT_000231b8 + 0x2318a,iVar1);
  }
  MonCtrl::ConPrintfMessage((char *)*puVar3,DAT_000231bc + 0x23196,(uint)local_19[0]);
  return local_19[0];
}


/* 000231c0 */

/* MprCtrlCnv::Init() */

void MprCtrlCnv::Init(void)

{
  return;
}


/* 000231c6 */

/* MprCtrlCnv::Exchg_DeviceType(MPR::DeviceType*, DefInfraMediaConfig::DeviceType*) */

void MprCtrlCnv::Exchg_DeviceType(DeviceType *param_1,DeviceType *param_2)

{
  undefined4 uVar1;
  
  switch(*(undefined4 *)param_2) {
  case 1:
    uVar1 = 2;
    break;
  case 2:
  case 3:
    uVar1 = 3;
    break;
  case 4:
    uVar1 = 4;
    break;
  case 5:
    uVar1 = 6;
    break;
  case 6:
    uVar1 = 8;
    break;
  case 7:
    uVar1 = 9;
    break;
  case 8:
    uVar1 = 7;
    break;
  default:
    uVar1 = 0;
  }
  *(undefined4 *)param_1 = uVar1;
  return;
}


/* 00023200 */

/* MprCtrlCnv::Exchg_DeviceType(DefInfraMediaConfig::DeviceType*, MPR::DeviceType*) */

void MprCtrlCnv::Exchg_DeviceType(DeviceType *param_1,DeviceType *param_2)

{
  undefined4 uVar1;
  
  switch(*(undefined4 *)param_2) {
  case 2:
    uVar1 = 1;
    break;
  case 3:
    uVar1 = 2;
    break;
  case 4:
    uVar1 = 4;
    break;
  default:
    uVar1 = 0;
    break;
  case 6:
    uVar1 = 5;
    break;
  case 7:
    uVar1 = 8;
    break;
  case 8:
    uVar1 = 6;
    break;
  case 9:
    uVar1 = 7;
  }
  *(undefined4 *)param_1 = uVar1;
  return;
}


/* 0002323a */

/* MprCtrlCnv::Exchg_StillAspect(MPR::SAspect*, UtilStillSize::ContentAspect*) */

void MprCtrlCnv::Exchg_StillAspect(SAspect *param_1,ContentAspect *param_2)

{
  uint uVar1;
  undefined4 uVar2;
  
  uVar1 = *(uint *)param_2;
  if (uVar1 == 2) {
    uVar2 = 1;
    goto LAB_0002326c;
  }
  if (uVar1 < 3) {
    uVar2 = 0;
    if (uVar1 == 0) goto LAB_0002326c;
    if (uVar1 == 1) {
      uVar2 = 2;
      goto LAB_0002326c;
    }
  }
  else if ((uVar1 == 3) || (uVar1 == 0xffffffff)) {
    *(undefined4 *)param_1 = 0;
    return;
  }
  uVar2 = 0;
LAB_0002326c:
  *(undefined4 *)param_1 = uVar2;
  return;
}


/* 00023270 */

/* MprCtrlCnv::Exchg_StillAspect(UtilStillSize::ContentAspect*, MPR::SAspect*) */

void MprCtrlCnv::Exchg_StillAspect(ContentAspect *param_1,SAspect *param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = *(int *)param_2;
  if (iVar1 == 1) {
    uVar2 = 2;
  }
  else if (iVar1 == 2) {
    uVar2 = 1;
  }
  else if (iVar1 == 0) {
    uVar2 = 0;
  }
  else {
    uVar2 = 0xffffffff;
  }
  *(undefined4 *)param_1 = uVar2;
  return;
}


/* 00023292 */

/* MprCtrl::_MediaInfo::SetMediaId(unsigned int) */

undefined4 __thiscall MprCtrl::_MediaInfo::SetMediaId(_MediaInfo *this,uint param_1)

{
  if (*(uint *)(this + 8) != param_1) {
    *(uint *)(this + 8) = param_1;
    return 0;
  }
  return 0xffffffff;
}


/* 000232a8 */

/* MprCtrl::SetSelfCheckLog(bool) */

void MprCtrl::SetSelfCheckLog(bool param_1)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 *puVar3;
  undefined2 uVar4;
  undefined2 *local_14 [2];
  
  puVar3 = *(undefined4 **)(DAT_0002330c + 0x232b4 + DAT_00023310);
  if (param_1) {
    uVar4 = 0x3122;
    MonCtrl::ConPutMessage((char *)*puVar3);
  }
  else {
    uVar4 = 0x2222;
    MonCtrl::ConPutMessage((char *)*puVar3);
  }
  iVar2 = osal_valloc_msg_wait(DAT_00023308,local_14,0x14,1);
  uVar1 = DAT_00023308;
  if (iVar2 == 0) {
    *local_14[0] = 199;
    local_14[0][3] = uVar4;
    local_14[0][1] = 0x9400;
    local_14[0][2] = 0xe;
    local_14[0][4] = 0;
    osal_snd_msg(uVar1);
  }
  return;
}


/* 0002331c */

/* MprCtrl::CallbackPoint(unsigned int, unsigned int, void*, unsigned int, void*) */

void MprCtrl::CallbackPoint(uint param_1,uint param_2,void *param_3,uint param_4,void *param_5)

{
  bool bVar1;
  int iVar2;
  uint uVar3;
  undefined4 *puVar4;
  int *piVar5;
  undefined1 auStack_20 [8];
  
  iVar2 = DAT_00023404 + 0x2332c;
  puVar4 = *(undefined4 **)(iVar2 + DAT_00023408);
  MonCtrl::ConPutMessage((char *)*puVar4);
  if (param_2 == DAT_000233fc) {
    MonCtrl::ConPutMessage((char *)*puVar4);
    if (*(int *)param_3 != 4) {
      return;
    }
    bVar1 = true;
  }
  else {
    if (param_2 != DAT_000233fc + 1) {
      if (param_2 != DAT_00023400) {
        return;
      }
      MonCtrl::ConPutMessage((char *)*puVar4);
      if (*(int *)param_3 == 0) {
        for (uVar3 = 0; uVar3 < *(uint *)((int)param_3 + 8); uVar3 = uVar3 + 1) {
          piVar5 = *(int **)(iVar2 + DAT_00023414);
          MWF::ObjLock::Lock((ObjLock *)(*piVar5 + 0x70));
          _MediaInfo::SetMediaId
                    ((_MediaInfo *)*piVar5,*(uint *)(*(int *)((int)param_3 + 4) + uVar3 * 4));
          MWF::ObjLock::Unlock((ObjLock *)(*piVar5 + 0x70));
        }
        **(uint **)(iVar2 + DAT_00023418) = *(uint *)((int)param_3 + 8);
      }
      MWF::ObjMsg::ObjMsg(auStack_20,0,0);
      (**(code **)(*(int *)**(undefined4 **)(iVar2 + DAT_0002341c) + 0xc))
                ((int *)**(undefined4 **)(iVar2 + DAT_0002341c),auStack_20);
      MWF::ObjMsg::~ObjMsg(auStack_20);
      return;
    }
    MonCtrl::ConPutMessage((char *)*puVar4);
    if (*(int *)param_3 != 4) {
      return;
    }
    bVar1 = false;
  }
  SetSelfCheckLog(bVar1);
  return;
}


/* 00023428 */

/* MprCtrl::PrintVersion() */

void MprCtrl::PrintVersion(void)

{
                    /* WARNING: Could not recover jumptable at 0x0001ef54. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*(code *)PTR_PrintVersion_0004be30)(2);
  return;
}


/* 00023438 */

/* MprCtrl::CnvEnterType(MprCtrl::EnterType) */

int MprCtrl::CnvEnterType(undefined4 param_1)

{
  switch(param_1) {
  case 0:
    return DAT_00023490 + 0x23454;
  case 1:
    return (int)&DAT_00023490 + DAT_000234b8;
  case 2:
    return DAT_00023494 + 0x2345a;
  case 3:
    return DAT_00023498 + 0x23460;
  case 4:
    return DAT_0002349c + 0x23466;
  case 5:
    return DAT_000234a0 + 0x2346c;
  case 6:
    return DAT_000234a4 + 0x23472;
  case 7:
    return DAT_000234a8 + 0x23478;
  case 8:
    return DAT_000234ac + 0x2347e;
  case 9:
    return DAT_000234b0 + 0x23484;
  default:
    return DAT_000234b4 + 0x2348a;
  }
}


/* 000234bc */

/* MprCtrl::CnvTvSystem(MPR::TvSystem) */

undefined * MprCtrl::CnvTvSystem(int param_1)

{
  if (param_1 == 0) {
    return (undefined *)(DAT_000234dc + 0x234ce);
  }
  if (param_1 == 1) {
    return &UNK_000234da + DAT_000234e4;
  }
  return (undefined *)(DAT_000234e0 + 0x234d4);
}


/* 000234e8 */

/* MprCtrl::CnvDeviceType(MPR::DeviceType) */

int MprCtrl::CnvDeviceType(undefined4 param_1)

{
  switch(param_1) {
  case 1:
    return DAT_00023534 + 0x23504;
  case 2:
    return (int)&DAT_00023534 + DAT_00023554;
  case 3:
    return DAT_00023538 + 0x2350a;
  case 4:
    return DAT_0002353c + 0x23510;
  case 5:
    return DAT_00023540 + 0x23516;
  case 6:
    return DAT_00023544 + 0x2351c;
  case 7:
    return DAT_00023548 + 0x23522;
  case 8:
    return DAT_0002354c + 0x23528;
  default:
    return DAT_00023550 + 0x2352e;
  }
}


/* 00023558 */

/* MprCtrl::PrintInfo(unsigned int) */

void MprCtrl::PrintInfo(uint param_1)

{
  undefined4 uVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  undefined4 *puVar5;
  int iVar6;
  char *pcVar7;
  int *piVar8;
  int iVar9;
  
  iVar6 = DAT_00023b78 + 0x2356c;
  puVar5 = *(undefined4 **)(iVar6 + DAT_00023b7c);
  MonCtrl::ConPrintfMessage((char *)*puVar5,DAT_00023b80 + 0x23576);
  if ((param_1 & 1) != 0) {
    MonCtrl::ConPrintfMessage((char *)*puVar5,DAT_00023b84 + 0x2358c);
    MonCtrl::ConPrintfMessage((char *)*puVar5,DAT_00023b88 + 0x23598);
    MonCtrl::ConPrintfMessage
              ((char *)*puVar5,DAT_00023b90 + 0x235aa,**(undefined4 **)(iVar6 + DAT_00023b8c));
    MonCtrl::ConPrintfMessage((char *)*puVar5,DAT_00023b94 + 0x235b8);
    pcVar7 = (char *)*puVar5;
    GetTvSystem();
    uVar1 = CnvTvSystem();
    MonCtrl::ConPrintfMessage(pcVar7,DAT_00023b98 + 0x235ce,uVar1);
    MonCtrl::ConPutMessageHeader();
    MonCtrl::ConPutStr((char *)*puVar5);
    uVar2 = GetSupportContentTypes();
    if ((uVar2 & 8) != 0) {
      MonCtrl::ConPutStr((char *)*puVar5);
    }
    if ((uVar2 & 0x10) != 0) {
      MonCtrl::ConPutStr((char *)*puVar5);
    }
    if ((uVar2 & 4) != 0) {
      MonCtrl::ConPutStr((char *)*puVar5);
    }
    if ((uVar2 & 0x80) != 0) {
      MonCtrl::ConPutStr((char *)*puVar5);
    }
    MonCtrl::ConPutStr((char *)*puVar5);
    MonCtrl::ConPutCRLF();
    MonCtrl::ConPutMessageHeader();
    MonCtrl::ConPutStr((char *)*puVar5);
    uVar2 = GetSupportMedia();
    if ((uVar2 & 2) != 0) {
      MonCtrl::ConPutStr((char *)*puVar5);
    }
    if ((uVar2 & 8) != 0) {
      MonCtrl::ConPutStr((char *)*puVar5);
    }
    MonCtrl::ConPutStr((char *)*puVar5);
    MonCtrl::ConPutCRLF();
    iVar3 = IsGpsSupport();
    if (iVar3 == 0) {
      pcVar7 = (char *)*puVar5;
      iVar3 = DAT_00023bc8 + 0x236ae;
    }
    else {
      pcVar7 = (char *)*puVar5;
      iVar3 = DAT_00023bc4 + 0x236a4;
    }
    MonCtrl::ConPrintfMessage(pcVar7,iVar3);
    iVar3 = IsMultiRecSupport();
    if (iVar3 == 0) {
      pcVar7 = (char *)*puVar5;
      iVar3 = DAT_00023bd0 + 0x236ca;
    }
    else {
      pcVar7 = (char *)*puVar5;
      iVar3 = DAT_00023bcc + 0x236c0;
    }
    MonCtrl::ConPrintfMessage(pcVar7,iVar3);
    iVar3 = IsCaptureIdTable();
    if (iVar3 == 0) {
      pcVar7 = (char *)*puVar5;
      iVar3 = DAT_00023bd8 + 0x236e6;
    }
    else {
      pcVar7 = (char *)*puVar5;
      iVar3 = DAT_00023bd4 + 0x236dc;
    }
    MonCtrl::ConPrintfMessage(pcVar7,iVar3);
    iVar3 = GetDualRecType();
    if (iVar3 == 0) {
      pcVar7 = (char *)*puVar5;
      iVar3 = DAT_00023bdc + 0x236f8;
    }
    else {
      pcVar7 = (char *)*puVar5;
      iVar3 = DAT_00023be0 + 0x23702;
    }
    MonCtrl::ConPrintfMessage(pcVar7,iVar3);
    pcVar7 = (char *)*puVar5;
    uVar1 = GetDualRecCaptureCount();
    MonCtrl::ConPrintfMessage(pcVar7,DAT_00023be4 + 0x23714,uVar1);
    iVar3 = IsDualRecOver18Mbps();
    if (iVar3 == 0) {
      pcVar7 = (char *)*puVar5;
      iVar3 = DAT_00023bec + 0x23734;
    }
    else {
      pcVar7 = (char *)*puVar5;
      iVar3 = DAT_00023be8 + 0x2372a;
    }
    MonCtrl::ConPrintfMessage(pcVar7,iVar3);
    iVar3 = IsDpofSupport();
    if (iVar3 == 0) {
      pcVar7 = (char *)*puVar5;
      iVar3 = DAT_00023bf4 + 0x23750;
    }
    else {
      pcVar7 = (char *)*puVar5;
      iVar3 = DAT_00023bf0 + 0x23746;
    }
    MonCtrl::ConPrintfMessage(pcVar7,iVar3);
    iVar3 = IsTcUbSupport();
    if (iVar3 == 0) {
      pcVar7 = (char *)*puVar5;
      iVar3 = DAT_00023bfc + 0x2376c;
    }
    else {
      pcVar7 = (char *)*puVar5;
      iVar3 = DAT_00023bf8 + 0x23762;
    }
    MonCtrl::ConPrintfMessage(pcVar7,iVar3);
    iVar3 = IsInternalFlashAviSupport();
    if (iVar3 == 0) {
      pcVar7 = (char *)*puVar5;
      iVar3 = DAT_00023c04 + 0x23788;
    }
    else {
      pcVar7 = (char *)*puVar5;
      iVar3 = DAT_00023c00 + 0x2377e;
    }
    MonCtrl::ConPrintfMessage(pcVar7,iVar3);
    iVar3 = IsSerialNumberRecSupport();
    if (iVar3 == 0) {
      MonCtrl::ConPrintfMessage((char *)*puVar5,DAT_00023c10 + 0x237be);
    }
    else {
      MonCtrl::ConPrintfMessage((char *)*puVar5,DAT_00023c08 + 0x2379a);
      pcVar7 = (char *)*puVar5;
      uVar1 = GetSerialNumber();
      MonCtrl::ConPrintfMessage(pcVar7,DAT_00023c0c + 0x237ac,uVar1);
    }
    iVar3 = IsDvMode();
    if (iVar3 == 0) {
      pcVar7 = (char *)*puVar5;
      iVar3 = DAT_00023c18 + 0x237da;
    }
    else {
      pcVar7 = (char *)*puVar5;
      iVar3 = DAT_00023c14 + 0x237d0;
    }
    MonCtrl::ConPrintfMessage(pcVar7,iVar3);
  }
  if ((param_1 & 2) != 0) {
    iVar3 = 0;
    MonCtrl::ConPrintfMessage((char *)*puVar5,DAT_00023c1c + 0x237f2);
    MonCtrl::ConPrintfMessage((char *)*puVar5,DAT_00023c20 + 0x237fe);
    do {
      MonCtrl::ConPrintfMessage((char *)*puVar5,DAT_00023c24 + 0x2380c,iVar3);
      piVar8 = *(int **)(iVar6 + DAT_00023c28);
      if (*(char *)(*piVar8 + iVar3 * 0x10) == '\0') {
        pcVar7 = (char *)*puVar5;
        iVar4 = DAT_00023c30 + 0x23838;
      }
      else {
        pcVar7 = (char *)*puVar5;
        iVar4 = DAT_00023c2c + 0x2382e;
      }
      MonCtrl::ConPrintfMessage(pcVar7,iVar4);
      iVar4 = iVar3 * 0x10;
      iVar3 = iVar3 + 1;
      MonCtrl::ConPrintfMessage
                ((char *)*puVar5,DAT_00023c34 + 0x2384c,*(undefined4 *)(*piVar8 + iVar4 + 4));
      MonCtrl::ConPrintfMessage
                ((char *)*puVar5,DAT_00023c38 + 0x23862,*(undefined4 *)(*piVar8 + iVar4 + 8));
      pcVar7 = (char *)*puVar5;
      uVar1 = CnvDeviceType(*(undefined4 *)(*piVar8 + iVar4 + 0xc));
      MonCtrl::ConPrintfMessage(pcVar7,DAT_00023c3c + 0x2387e,uVar1);
    } while (iVar3 != 5);
    iVar3 = 0;
    MonCtrl::ConPrintfMessage((char *)*puVar5,DAT_00023c40 + 0x23896);
    do {
      MonCtrl::ConPrintfMessage((char *)*puVar5,DAT_00023c44 + 0x238a2,iVar3);
      if (*(char *)(*piVar8 + iVar3 * 0x10 + 0x50) == '\0') {
        pcVar7 = (char *)*puVar5;
        iVar4 = DAT_00023c4c + 0x238c2;
      }
      else {
        pcVar7 = (char *)*puVar5;
        iVar4 = DAT_00023c48 + 0x238ba;
      }
      MonCtrl::ConPrintfMessage(pcVar7,iVar4);
      iVar9 = iVar3 * 0x10;
      iVar4 = iVar3 * 0x10;
      iVar3 = iVar3 + 1;
      MonCtrl::ConPrintfMessage
                ((char *)*puVar5,DAT_00023c50 + 0x238d8,*(undefined4 *)(*piVar8 + iVar4 + 0x54));
      MonCtrl::ConPrintfMessage
                ((char *)*puVar5,DAT_00023c54 + 0x238ee,*(undefined4 *)(*piVar8 + iVar9 + 0x58));
      pcVar7 = (char *)*puVar5;
      uVar1 = CnvDeviceType(*(undefined4 *)(*piVar8 + iVar9 + 0x5c));
      MonCtrl::ConPrintfMessage(pcVar7,DAT_00023c58 + 0x23908,uVar1);
    } while (iVar3 != 2);
  }
  if ((param_1 & 4) != 0) {
    MprCtrlStillMgr::PrintStillSize();
  }
  if ((param_1 & 8) != 0) {
    MprCtrlStillMgr::PrintStillData((MprCtrlStillMgr *)**(undefined4 **)(iVar6 + DAT_00023c5c));
  }
  if ((param_1 & 0x10) != 0) {
    MprCtrlStillMgr::PrintStillBackup((MprCtrlStillMgr *)**(undefined4 **)(iVar6 + DAT_00023c5c));
  }
  if ((param_1 & 0x20) != 0) {
    MonCtrl::ConPrintfMessage((char *)*puVar5,DAT_00023c60 + 0x23956);
    MonCtrl::ConPrintfMessage((char *)*puVar5,DAT_00023c64 + 0x23960);
    iVar3 = 0;
    do {
      iVar4 = iVar3 + 1;
      MonCtrl::ConPrintfMessage
                ((char *)*puVar5,DAT_00023c6c + 0x23970,iVar3,
                 *(undefined4 *)(**(int **)(iVar6 + DAT_00023c68) + iVar3 * 4));
      iVar3 = iVar4;
    } while (iVar4 != 3);
  }
  if ((param_1 & 0x40) == 0) {
    return;
  }
  MonCtrl::ConPrintfMessage((char *)*puVar5,DAT_00023c70 + 0x23992);
  MonCtrl::ConPrintfMessage((char *)*puVar5,DAT_00023c74 + 0x2399c);
  piVar8 = *(int **)(iVar6 + DAT_00023c78);
  MonCtrl::ConPrintfMessage
            ((char *)*puVar5,DAT_00023c7c + 0x239aa,**(undefined4 **)(*piVar8 + 0x40));
  MonCtrl::ConPrintfMessage
            ((char *)*puVar5,DAT_00023c80 + 0x239be,*(undefined4 *)(*(int *)(*piVar8 + 0x40) + 4));
  if (*(int *)(*(int *)(*piVar8 + 0x40) + 4) != 0) {
    MonCtrl::ConPrintfMessage((char *)*puVar5,DAT_00023c84 + 0x239d2);
  }
  for (uVar2 = 0; uVar2 < *(uint *)(*(int *)(*piVar8 + 0x40) + 4); uVar2 = uVar2 + 1) {
    iVar6 = uVar2 * 0x1c;
    MonCtrl::ConPrintfMessage
              ((char *)*puVar5,DAT_00023c88 + 0x239e8,
               *(undefined4 *)(*(int *)(*piVar8 + 0x40) + iVar6 + 0x10));
    MonCtrl::ConPrintfMessage
              ((char *)*puVar5,DAT_00023c8c + 0x239fe,
               *(undefined4 *)(*(int *)(*piVar8 + 0x40) + iVar6 + 8));
    MonCtrl::ConPrintfMessage
              ((char *)*puVar5,DAT_00023c90 + 0x23a10,
               *(undefined4 *)(*(int *)(*piVar8 + 0x40) + iVar6 + 0xc));
    MonCtrl::ConPrintfMessage
              ((char *)*puVar5,DAT_00023c94 + 0x23a22,
               (uint)*(ushort *)(*(int *)(*piVar8 + 0x40) + iVar6 + 0x18));
    MonCtrl::ConPrintfMessage
              ((char *)*puVar5,DAT_00023c98 + 0x23a34,
               *(undefined4 *)(*(int *)(*piVar8 + 0x40) + iVar6 + 0x14));
    MonCtrl::ConPrintfMessage
              ((char *)*puVar5,DAT_00023c9c + 0x23a46,
               *(undefined4 *)(*(int *)(*piVar8 + 0x40) + iVar6 + 0x1c));
  }
  MonCtrl::ConPrintfMessage((char *)*puVar5,DAT_00023ca0 + 0x23a5e);
  MonCtrl::ConPrintfMessage
            ((char *)*puVar5,DAT_00023ca4 + 0x23a6c,*(undefined4 *)(*(int *)(*piVar8 + 0x40) + 0x6c)
            );
  MonCtrl::ConPrintfMessage
            ((char *)*puVar5,DAT_00023ca8 + 0x23a7c,*(undefined4 *)(*(int *)(*piVar8 + 0x40) + 0x70)
            );
  MonCtrl::ConPrintfMessage((char *)*puVar5,DAT_00023cac + 0x23a88);
  MonCtrl::ConPrintfMessage
            ((char *)*puVar5,DAT_00023cb0 + 0x23a96,*(undefined4 *)(*(int *)(*piVar8 + 0x40) + 0x68)
            );
  MonCtrl::ConPrintfMessage
            ((char *)*puVar5,DAT_00023cb4 + 0x23aa6,*(undefined4 *)(*(int *)(*piVar8 + 0x40) + 0x60)
            );
  MonCtrl::ConPrintfMessage((char *)*puVar5,DAT_00023cb8 + 0x23ab6,*(undefined4 *)(*piVar8 + 4));
  if (*(int *)(*piVar8 + 4) == 0) {
    MonCtrl::ConPrintfMessage((char *)*puVar5,DAT_00023cbc + 0x23ac6);
  }
  else {
    MonCtrl::ConPutMessageHeader();
    MonCtrl::ConPrintf((char *)*puVar5,DAT_00023cc0 + 0x23ad8);
    if ((*(uint *)(*piVar8 + 4) & 2) == 0) {
      pcVar7 = (char *)*puVar5;
      iVar6 = DAT_00023cc8 + 0x23af4;
    }
    else {
      pcVar7 = (char *)*puVar5;
      iVar6 = DAT_00023cc4 + 0x23aec;
    }
    MonCtrl::ConPrintf(pcVar7,iVar6);
    MonCtrl::ConPutMessageHeader();
    MonCtrl::ConPrintf((char *)*puVar5,DAT_00023ccc + 0x23b04);
    if ((*(uint *)(*piVar8 + 4) & 1) == 0) {
      pcVar7 = (char *)*puVar5;
      iVar6 = DAT_00023cd4 + 0x23b20;
    }
    else {
      pcVar7 = (char *)*puVar5;
      iVar6 = DAT_00023cd0 + 0x23b18;
    }
    MonCtrl::ConPrintf(pcVar7,iVar6);
  }
  MonCtrl::ConPrintfMessage((char *)*puVar5,DAT_00023cd8 + 0x23b2e,*(undefined4 *)(*piVar8 + 0x24));
  MonCtrl::ConPrintfMessage((char *)*puVar5,DAT_00023cdc + 0x23b3c,*(undefined4 *)(*piVar8 + 0x20));
  MonCtrl::ConPrintfMessage((char *)*puVar5,DAT_00023ce0 + 0x23b46);
  MonCtrl::ConPrintfMessage((char *)*puVar5,DAT_00023ce4 + 0x23b54,*(undefined4 *)(*piVar8 + 0x1c));
  (*(code *)PTR_ConPrintfMessage_0004c114)
            (*puVar5,DAT_00023ce8 + 0x23b60,*(undefined4 *)(*piVar8 + 0x18));
  return;
}


/* 00023cec */

void InfraMprCtrl_Init(void)

{
  MprCtrl::Init();
  (*(code *)PTR_RegisterCommand_0004c104)();
  return;
}


/* 00023cfc */

void InfraMprCtrl_Fin(void)

{
  MprCtrlMcmd::UnregisterCommand();
                    /* WARNING: Could not recover jumptable at 0x0001f568. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*(code *)PTR_Destroy_0004c01c)();
  return;
}


/* 00023d0c */

undefined4 mprctrl_RegisterCommand(void)

{
  MprCtrlMcmd::RegisterCommand();
  return 0;
}


/* 00023d18 */

undefined4 mprctrl_UnregisterCommand(void)

{
  MprCtrlMcmd::UnregisterCommand();
  return 0;
}


/* 00023d24 */

/* StrUtil::StrCmp(char const*, char const*) */

void StrUtil::StrCmp(char *param_1,char *param_2)

{
  (*(code *)PTR_strcmp_0004c2e4)(param_1);
  return;
}


/* 00023d30 */

/* MprCtrlLog::SetBasicLog(unsigned char, unsigned short, unsigned short) */

void MprCtrlLog::SetBasicLog(uchar param_1,ushort param_2,ushort param_3)

{
  Log::Set(2,199,1,param_2 | param_1,param_3,0);
  return;
}


/* 00023d4e */

/* MprCtrlLog::SetStartApiLog(unsigned char, unsigned short) */

void MprCtrlLog::SetStartApiLog(uchar param_1,ushort param_2)

{
  (*(code *)PTR_SetBasicLog_0004bf1c)(param_1,0x100,param_2);
  return;
}


/* 00023d60 */

/* MprCtrlLog::SetLog(unsigned short, unsigned short, unsigned short, unsigned short) */

void MprCtrlLog::SetLog(ushort param_1,ushort param_2,ushort param_3,ushort param_4)

{
  Log::Set(2,199,param_1,param_2,param_3,param_4);
  return;
}


/* 00023d7e */

/* MprCtrlLog::SetMemoryMapLog(unsigned int) */

void MprCtrlLog::SetMemoryMapLog(uint param_1)

{
                    /* WARNING: Could not recover jumptable at 0x0001f4f8. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*(code *)PTR_SetLog_0004bff8)(9,param_1 >> 0x10,param_1 & 0xffff,0);
  return;
}


/* 00023d94 */

/* MprCtrlLog::SetUnitTypeLog(unsigned char, unsigned int, unsigned short) */

void MprCtrlLog::SetUnitTypeLog(uchar param_1,uint param_2,ushort param_3)

{
  SetBasicLog(param_1,0x800,param_3);
                    /* WARNING: Could not recover jumptable at 0x0001f4f8. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*(code *)PTR_SetLog_0004bff8)(8,param_2 >> 0x10,param_2 & 0xffff,0);
  return;
}


/* 00023db2 */

/* MprCtrlLog::SetUnitHandleLog(unsigned char, unsigned short, unsigned short) */

void MprCtrlLog::SetUnitHandleLog(uchar param_1,ushort param_2,ushort param_3)

{
  SetBasicLog(param_1,0x900,param_3);
                    /* WARNING: Could not recover jumptable at 0x0001f4f8. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*(code *)PTR_SetLog_0004bff8)(7,param_2,0,0);
  return;
}


/* 00023dd0 */

/* MprCtrlLog::SetSendEventLog(unsigned char, unsigned int, unsigned short) */

void MprCtrlLog::SetSendEventLog(uchar param_1,uint param_2,ushort param_3)

{
                    /* WARNING: Could not recover jumptable at 0x0001f4f8. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*(code *)PTR_SetLog_0004bff8)(6,param_2 >> 0x10,param_2 & 0xffff,0);
  return;
}


/* 00023de6 */

/* MprCtrlLog::SetRsrcLog(unsigned char, unsigned int, unsigned short) */

void MprCtrlLog::SetRsrcLog(uchar param_1,uint param_2,ushort param_3)

{
  SetBasicLog(param_1,0x600,param_3);
                    /* WARNING: Could not recover jumptable at 0x0001f4f8. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*(code *)PTR_SetLog_0004bff8)(5,param_2 >> 0x10,param_2 & 0xffff,0);
  return;
}


/* 00023e04 */

/* MprCtrlLog::SetParamLog(unsigned char, unsigned short, unsigned short, unsigned short, unsigned
   short) */

void MprCtrlLog::SetParamLog
               (uchar param_1,ushort param_2,ushort param_3,ushort param_4,ushort param_5)

{
  SetBasicLog(param_1,0x500,param_5);
                    /* WARNING: Could not recover jumptable at 0x0001f4f8. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*(code *)PTR_SetLog_0004bff8)(4,param_2,param_3,param_4);
  return;
}


/* 00023e2a */

/* MprCtrlLog::SetStateLog(unsigned char, unsigned short, unsigned short, unsigned short) */

void MprCtrlLog::SetStateLog(uchar param_1,ushort param_2,ushort param_3,ushort param_4)

{
  SetBasicLog(param_1,0x400,param_4);
                    /* WARNING: Could not recover jumptable at 0x0001f4f8. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*(code *)PTR_SetLog_0004bff8)(3,param_2,param_3,0);
  return;
}


/* 00023e4c */

/* MprCtrlLog::CnvFileNameToId(char const*) */

undefined2 MprCtrlLog::CnvFileNameToId(char *param_1)

{
  char *pcVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  if (param_1 == (char *)0x0) {
    return 0xffff;
  }
  iVar3 = 0;
  pcVar1 = strstr(param_1,(char *)(DAT_00023e90 + 0x23e5c));
  if (pcVar1 != (char *)0x0) {
    param_1 = pcVar1;
  }
  do {
    iVar4 = DAT_00023e94 + 0x23e6c;
    iVar2 = StrUtil::StrCmp(*(char **)(iVar4 + iVar3 * 8 + 4),param_1);
    if (iVar2 == 0) {
      return *(undefined2 *)(iVar4 + iVar3 * 8);
    }
    iVar3 = iVar3 + 1;
  } while (iVar3 != 9);
  return 0xffff;
}


/* 00023e98 */

/* MprCtrlLog::SetErrLog(unsigned char, unsigned int, unsigned short, char const*) */

void MprCtrlLog::SetErrLog(uchar param_1,uint param_2,ushort param_3,char *param_4)

{
  undefined4 uVar1;
  
  SetBasicLog(param_1,0x300,param_3);
  uVar1 = CnvFileNameToId(param_4);
                    /* WARNING: Could not recover jumptable at 0x0001f4f8. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*(code *)PTR_SetLog_0004bff8)(2,param_2 >> 0x10,param_2 & 0xffff,uVar1);
  return;
}


/* 00023ebe */

/* MprCtrlLog::SetEndApiLog(unsigned char, unsigned int, unsigned short) */

void MprCtrlLog::SetEndApiLog(uchar param_1,uint param_2,ushort param_3)

{
  undefined4 uVar1;
  
  SetBasicLog(param_1,0x200,param_3);
  if (param_2 == 0) {
    return;
  }
  uVar1 = CnvFileNameToId((char *)0x0);
                    /* WARNING: Could not recover jumptable at 0x0001f4f8. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*(code *)PTR_SetLog_0004bff8)(2,param_2 >> 0x10,param_2 & 0xffff,uVar1);
  return;
}


/* 00023ee6 */

/* StrUtil::StrCat(char*, char const*) */

char * StrUtil::StrCat(char *param_1,char *param_2)

{
  size_t sVar1;
  size_t sVar2;
  
  sVar1 = strlen(param_1);
  sVar2 = strlen(param_2);
  memcpy(param_1 + sVar1,param_2,sVar2 + 1);
  return param_1;
}


/* 00023f08 */

/* StrUtil::StrrChr(char const*, unsigned int) */

void StrUtil::StrrChr(char *param_1,uint param_2)

{
  (*(code *)PTR_strrchr_0004be08)(param_1);
  return;
}


/* 00023f14 */

/* MprCtrl::GetMediaInfo(unsigned int, MprCtrl::_MediaConfigInfo*) */

int MprCtrl::GetMediaInfo(uint param_1,_MediaConfigInfo *param_2)

{
  undefined4 uVar1;
  undefined4 *puVar2;
  int iVar3;
  char *pcVar4;
  int iVar5;
  int iVar6;
  undefined4 *puVar7;
  _MediaConfigInfo *p_Var8;
  undefined4 *puVar9;
  undefined4 local_114;
  undefined2 local_110;
  undefined2 local_10e;
  uint local_fc;
  undefined4 *local_30;
  undefined4 local_2c [2];
  
  iVar6 = DAT_000241f8 + 0x23f24;
  local_2c[0] = 0;
  local_30 = (undefined4 *)0x0;
  puVar7 = *(undefined4 **)(iVar6 + DAT_000241fc);
  MonCtrl::ConPrintfMessage((char *)*puVar7,DAT_00024200 + 0x23f3c,param_1);
  MemUtil::MemSet8(&local_114,'\0',0xe4);
  local_114 = 0x1000;
  local_110 = 3;
  local_10e = 0xcc;
  local_fc = param_1;
  iVar3 = osal_dynamic_id(0x2a,199,local_2c);
  if (iVar3 == 0) {
    iVar3 = osal_valloc_msg_wait(DAT_000241f4,&local_30,0xe4,1);
    if (iVar3 == 0) {
      MemUtil::MemCpy8(local_30,&local_114,0xe4);
      uVar1 = DAT_000241f4;
      local_30[-1] = local_2c[0];
      iVar3 = osal_snd_sync_msg(uVar1);
      if (iVar3 == 0) {
        MonCtrl::ConPrintfMessage((char *)*puVar7,DAT_00024214 + 0x23fd2);
        puVar2 = local_30;
        MonCtrl::ConPrintfMessage((char *)*puVar7,DAT_00024218 + 0x23fe0);
        MonCtrl::ConPrintfMessage((char *)*puVar7,DAT_0002421c + 0x23fec,*puVar2);
        MonCtrl::ConPrintfMessage
                  ((char *)*puVar7,DAT_00024220 + 0x23ffa,(uint)*(ushort *)(puVar2 + 1));
        MonCtrl::ConPrintfMessage
                  ((char *)*puVar7,DAT_00024224 + 0x24006,(uint)*(ushort *)((int)puVar2 + 6));
        MonCtrl::ConPrintfMessage((char *)*puVar7,DAT_00024228 + 0x24012,puVar2[5]);
        MonCtrl::ConPrintfMessage((char *)*puVar7,DAT_0002422c + 0x2401e,puVar2[6]);
        MonCtrl::ConPrintfMessage
                  ((char *)*puVar7,DAT_00024230 + 0x2402a,(uint)*(ushort *)((int)puVar2 + 0x1e));
        MonCtrl::ConPrintfMessage((char *)*puVar7,DAT_00024234 + 0x2403a,puVar2 + 8);
        MonCtrl::ConPrintfMessage((char *)*puVar7,DAT_00024238 + 0x24044,puVar2[0xe]);
        MonCtrl::ConPrintfMessage
                  ((char *)*puVar7,DAT_0002423c + 0x24050,(uint)*(byte *)(puVar2 + 0xf));
        iVar6 = 0;
        puVar9 = puVar2;
        while( true ) {
          if ((int)(uint)*(byte *)(puVar2 + 0xf) <= iVar6) break;
          MonCtrl::ConPrintfMessage((char *)*puVar7,DAT_00024240 + 0x24062,iVar6,puVar9[0x10]);
          MonCtrl::ConPrintfMessage
                    ((char *)*puVar7,DAT_00024244 + 0x24072,iVar6,(uint)*(ushort *)(puVar9 + 0x11));
          iVar6 = iVar6 + 1;
          puVar9 = puVar9 + 2;
        }
        MonCtrl::ConPrintfMessage
                  ((char *)*puVar7,DAT_00024248 + 0x24092,(uint)*(byte *)(puVar2 + 0x18));
        MonCtrl::ConPrintfMessage
                  ((char *)*puVar7,DAT_0002424c + 0x240a0,(uint)*(byte *)((int)puVar2 + 0x61));
        MonCtrl::ConPrintfMessage
                  ((char *)*puVar7,DAT_00024250 + 0x240ae,(uint)*(byte *)((int)puVar2 + 0x62));
        MonCtrl::ConPrintfMessage
                  ((char *)*puVar7,DAT_00024254 + 0x240bc,(uint)*(byte *)((int)puVar2 + 99));
        MonCtrl::ConPrintfMessage
                  ((char *)*puVar7,DAT_00024258 + 0x240ca,(uint)*(byte *)(puVar2 + 0x20));
        MonCtrl::ConPrintfMessage
                  ((char *)*puVar7,DAT_0002425c + 0x240d8,(uint)*(byte *)((int)puVar2 + 0x81));
        MonCtrl::ConPrintfMessage
                  ((char *)*puVar7,DAT_00024260 + 0x240e6,(uint)*(byte *)((int)puVar2 + 0x82));
        MonCtrl::ConPrintfMessage
                  ((char *)*puVar7,DAT_00024264 + 0x240f4,(uint)*(byte *)(puVar2 + 0x22));
        MonCtrl::ConPrintfMessage
                  ((char *)*puVar7,DAT_00024268 + 0x24102,(uint)*(byte *)((int)puVar2 + 0x87));
        MonCtrl::ConPrintfMessage
                  ((char *)*puVar7,DAT_0002426c + 0x24110,(uint)*(byte *)((int)puVar2 + 0x89));
        MonCtrl::ConPrintfMessage
                  ((char *)*puVar7,DAT_00024270 + 0x2411e,(uint)*(byte *)(puVar2 + 0x28));
        MonCtrl::ConPrintfMessage
                  ((char *)*puVar7,DAT_00024274 + 0x2412c,(uint)*(byte *)((int)puVar2 + 0xa1));
        MonCtrl::ConPrintfMessage
                  ((char *)*puVar7,DAT_00024278 + 0x2413a,(uint)*(byte *)((int)puVar2 + 0xa2));
        MonCtrl::ConPrintfMessage
                  ((char *)*puVar7,DAT_0002427c + 0x24148,(uint)*(byte *)((int)puVar2 + 0xa3));
        MonCtrl::ConPrintfMessage
                  ((char *)*puVar7,DAT_00024280 + 0x2415a,(uint)*(byte *)(puVar2 + 0x29));
        iVar6 = 0;
        MonCtrl::ConPrintfMessage((char *)*puVar7,DAT_00024284 + 0x24166);
        *param_2 = *(_MediaConfigInfo *)(puVar2 + 7);
        *(undefined2 *)(param_2 + 2) = *(undefined2 *)((int)puVar2 + 0x1e);
        MprCtrlCnv::Exchg_DeviceType(param_2 + 0x1c,(DeviceType *)(puVar2 + 0xe));
        param_2[0x20] = *(_MediaConfigInfo *)(puVar2 + 0xf);
        p_Var8 = param_2;
        puVar7 = puVar2;
        while( true ) {
          if ((int)(uint)(byte)param_2[0x20] <= iVar6) break;
          MprCtrlCnv::Exchg_DeviceType
                    (param_2 + iVar6 * 8 + 0x24,(DeviceType *)(puVar2 + iVar6 * 2 + 0x10));
          iVar6 = iVar6 + 1;
          *(undefined2 *)(p_Var8 + 0x28) = *(undefined2 *)(puVar7 + 0x11);
          p_Var8 = p_Var8 + 8;
          puVar7 = puVar7 + 2;
        }
        MemUtil::MemCpy8(param_2 + 4,puVar2 + 8,0x15);
        MemUtil::MemCpy8(param_2 + 0x44,puVar2 + 0x18,0x80);
        goto LAB_000241d0;
      }
      iVar5 = DAT_00024210 + 0x23fc6;
      pcVar4 = (char *)**(undefined4 **)(iVar6 + DAT_00024204);
    }
    else {
      iVar5 = DAT_0002420c + 0x23f92;
      pcVar4 = (char *)**(undefined4 **)(iVar6 + DAT_00024204);
    }
  }
  else {
    iVar5 = DAT_00024208 + 0x23f74;
    pcVar4 = (char *)**(undefined4 **)(iVar6 + DAT_00024204);
  }
  MonCtrl::ConPrintfMessage(pcVar4,iVar5,iVar3);
LAB_000241d0:
  if (local_30 != (undefined4 *)0x0) {
    osal_free_msg(DAT_000241f4);
  }
  osal_dynamic_id(0x4a,0,local_2c[0]);
  return iVar3;
}


/* 00024288 */

/* MprCtrl::GetCreateMMgrType(MprCtrl::_MediaConfigInfo*) */

undefined4 MprCtrl::GetCreateMMgrType(_MediaConfigInfo *param_1)

{
  undefined4 uVar1;
  undefined4 *puVar2;
  
  puVar2 = *(undefined4 **)(DAT_00024310 + 0x24290 + DAT_00024314);
  MonCtrl::ConPrintfMessage((char *)*puVar2,DAT_00024318 + 0x2429c);
  switch(*(undefined4 *)(param_1 + 0x1c)) {
  case 2:
    uVar1 = 1;
    break;
  case 3:
    if (param_1[0x66] == (_MediaConfigInfo)0x0) {
      uVar1 = 2;
    }
    else {
      uVar1 = 4;
    }
    break;
  case 4:
    uVar1 = 5;
    break;
  default:
    uVar1 = 0xff;
    break;
  case 6:
    if (param_1[0x6d] == (_MediaConfigInfo)0x0) {
      uVar1 = 3;
    }
    else {
      uVar1 = 6;
    }
    break;
  case 7:
    uVar1 = 0;
    break;
  case 8:
    if ((param_1[0x66] == (_MediaConfigInfo)0x0) && (param_1[0x6c] == (_MediaConfigInfo)0x0)) {
      if (param_1[0x84] == (_MediaConfigInfo)0x0) {
        uVar1 = 0xff;
      }
      else {
        uVar1 = 7;
      }
    }
    else {
      uVar1 = 4;
    }
    break;
  case 9:
    uVar1 = 6;
  }
  MonCtrl::ConPrintfMessage((char *)*puVar2,DAT_0002431c + 0x2430a,uVar1);
  return uVar1;
}


/* 00024320 */

/* MprCtrl::CreatePrefix(char*, char*) */

void MprCtrl::CreatePrefix(char *param_1,char *param_2)

{
  int iVar1;
  undefined4 *puVar2;
  
  puVar2 = *(undefined4 **)(DAT_0002436c + 0x24328 + DAT_00024370);
  MonCtrl::ConPrintfMessage((char *)*puVar2,DAT_00024374 + 0x24338);
  iVar1 = StrUtil::StrrChr(param_1,0x2f);
  if (iVar1 != 0) {
    MemUtil::MemCpy8(param_2,(void *)(iVar1 + 1),0x10);
    StrUtil::StrCat(param_2,(char *)(DAT_00024378 + 0x2435a));
  }
  (*(code *)PTR_ConPrintfMessage_0004c114)(*puVar2,DAT_0002437c + 0x24366,param_2);
  return;
}


/* 00024380 */

/* MprCtrlMcmd::CtrlPrintAllMemTbl(int, char**) */

undefined4 MprCtrlMcmd::CtrlPrintAllMemTbl(int param_1,char **param_2)

{
  DmmAccess::PrintAllModeTable();
  return 1;
}


/* 0002438c */

/* MprCtrlMcmd::CtrlPrintMemTbl(int, char**) */

undefined4 MprCtrlMcmd::CtrlPrintMemTbl(int param_1,char **param_2)

{
  ushort uVar1;
  
  if (param_1 < 2) {
    MonCtrl::ConPutStr((char *)**(undefined4 **)(DAT_000243b8 + 0x24396 + DAT_000243bc));
  }
  else {
    uVar1 = StrUtil::StrDecToUInt32(param_2[1]);
    DmmAccess::PrintModeTable((uint)uVar1);
  }
  return 1;
}


/* 000243c4 */

/* MprCtrlMcmd::CtrlShareUnit(int, char**) */

undefined4 MprCtrlMcmd::CtrlShareUnit(int param_1,char **param_2)

{
  ushort uVar1;
  int iVar2;
  uint uVar3;
  uchar *puVar4;
  undefined4 uVar5;
  int iVar6;
  char *pcVar7;
  
  iVar6 = DAT_00024440 + 0x243d2;
  if (param_1 < 3) {
    MonCtrl::ConPutStr((char *)**(undefined4 **)(iVar6 + DAT_00024444));
  }
  else {
    iVar2 = StrUtil::StrHexToUInt32(param_2[3]);
    if (iVar2 == 1) {
      uVar3 = StrUtil::StrHexToUInt32(param_2[1]);
      uVar1 = StrUtil::StrHexToUInt32(param_2[2]);
      puVar4 = (uchar *)DmmAccess::DmmShareAndOpen(uVar3,uVar1);
    }
    else {
      uVar3 = StrUtil::StrHexToUInt32(param_2[1]);
      uVar1 = StrUtil::StrHexToUInt32(param_2[2]);
      puVar4 = (uchar *)DmmAccess::DmmShare(uVar3,uVar1);
    }
    if (puVar4 != (uchar *)0x0) {
      pcVar7 = (char *)**(undefined4 **)(iVar6 + DAT_00024444);
      uVar5 = DmmAccess::GetUnitHandle(puVar4);
      MonCtrl::ConPrintf(pcVar7,DAT_0002444c + 0x2442e,uVar5);
      DmmAccess::BufFree(puVar4);
    }
  }
  return 1;
}


/* 00024450 */

/* MprCtrlMcmd::CtrlReuseUnit(int, char**) */

undefined4 MprCtrlMcmd::CtrlReuseUnit(int param_1,char **param_2)

{
  ushort uVar1;
  uint uVar2;
  uchar *puVar3;
  undefined4 uVar4;
  int iVar5;
  char *pcVar6;
  
  iVar5 = DAT_000244a8 + 0x2445e;
  if (param_1 < 3) {
    MonCtrl::ConPutStr((char *)**(undefined4 **)(iVar5 + DAT_000244ac));
  }
  else {
    uVar2 = StrUtil::StrHexToUInt32(param_2[1]);
    uVar1 = StrUtil::StrHexToUInt32(param_2[2]);
    puVar3 = (uchar *)DmmAccess::DmmReuseAndOpen(uVar2,uVar1);
    if (puVar3 != (uchar *)0x0) {
      pcVar6 = (char *)**(undefined4 **)(iVar5 + DAT_000244ac);
      uVar4 = DmmAccess::GetUnitHandle(puVar3);
      MonCtrl::ConPrintf(pcVar6,DAT_000244b4 + 0x24498,uVar4);
      DmmAccess::BufFree(puVar3);
    }
  }
  return 1;
}


/* 000244b8 */

/* MprCtrlMcmd::CtrlFreeUnit(int, char**) */

undefined4 MprCtrlMcmd::CtrlFreeUnit(int param_1,char **param_2)

{
  ushort uVar1;
  
  if (param_1 < 2) {
    MonCtrl::ConPutStr((char *)**(undefined4 **)(DAT_000244e4 + 0x244c2 + DAT_000244e8));
  }
  else {
    uVar1 = StrUtil::StrHexToUInt32(param_2[1]);
    DmmAccess::DmmCloseAndFree(uVar1);
  }
  return 1;
}


/* 000244f0 */

/* MprCtrlMcmd::CtrlAllocUnit(int, char**) */

undefined4 MprCtrlMcmd::CtrlAllocUnit(int param_1,char **param_2)

{
  uint uVar1;
  uchar *puVar2;
  undefined4 uVar3;
  int iVar4;
  char *pcVar5;
  
  iVar4 = DAT_0002453c + 0x244fc;
  if (param_1 < 2) {
    MonCtrl::ConPutStr((char *)**(undefined4 **)(iVar4 + DAT_00024540));
  }
  else {
    uVar1 = StrUtil::StrHexToUInt32(param_2[1]);
    puVar2 = (uchar *)DmmAccess::DmmAllocateAndOpen(uVar1);
    if (puVar2 != (uchar *)0x0) {
      pcVar5 = (char *)**(undefined4 **)(iVar4 + DAT_00024540);
      uVar3 = DmmAccess::GetUnitHandle(puVar2);
      MonCtrl::ConPrintf(pcVar5,DAT_00024548 + 0x2452a,uVar3);
      DmmAccess::BufFree(puVar2);
    }
  }
  return 1;
}


/* 0002454c */

/* MprCtrlMcmd::CtrlFreeDmmMemory(int, char**) */

undefined4 MprCtrlMcmd::CtrlFreeDmmMemory(int param_1,char **param_2)

{
  char *pcVar1;
  int iVar2;
  uint uVar3;
  undefined4 *puVar4;
  
  puVar4 = *(undefined4 **)(DAT_000245b4 + 0x2455c + DAT_000245b8);
  if (param_1 < 2) {
    pcVar1 = (char *)*puVar4;
  }
  else if (param_1 == 2) {
    iVar2 = StrUtil::StrHexToUInt32(param_2[1]);
    iVar2 = DmmAccess::FreeDmmMemory(iVar2);
    if (iVar2 == 0) {
      pcVar1 = (char *)*puVar4;
    }
    else {
      pcVar1 = (char *)*puVar4;
    }
  }
  else {
    iVar2 = StrUtil::StrHexToUInt32(param_2[1]);
    uVar3 = StrUtil::StrHexToUInt32(param_2[2]);
    iVar2 = DmmAccess::FreeDmmMemory(iVar2,uVar3);
    if (iVar2 == 0) {
      pcVar1 = (char *)*puVar4;
    }
    else {
      pcVar1 = (char *)*puVar4;
    }
  }
  MonCtrl::ConPutStr(pcVar1);
  return 1;
}


/* 000245d0 */

/* MprCtrlMcmd::CtrlAllocDmmMemory(int, char**) */

undefined4 MprCtrlMcmd::CtrlAllocDmmMemory(int param_1,char **param_2)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 *puVar3;
  ushort auStack_12 [3];
  
  puVar3 = *(undefined4 **)(DAT_00024610 + 0x245de + DAT_00024614);
  if (param_1 < 2) {
    MonCtrl::ConPutStr((char *)*puVar3);
  }
  else {
    iVar1 = StrUtil::StrHexToUInt32(param_2[1]);
    uVar2 = DmmAccess::AllocDmmMemory(iVar1,auStack_12);
    MonCtrl::ConPrintf((char *)*puVar3,DAT_0002461c + 0x24600,uVar2);
  }
  return 1;
}


/* 00024620 */

/* MprCtrlMcmd::CtrlCalcStillData(int, char**) */

undefined4 MprCtrlMcmd::CtrlCalcStillData(int param_1,char **param_2)

{
  MprCtrlStillMgr::CreateStillData
            ((MprCtrlStillMgr *)**(undefined4 **)(DAT_00024638 + 0x24628 + DAT_0002463c));
  return 1;
}


/* 00024640 */

/* MprCtrlMcmd::CtrlGetStillEdit(int, char**) */

undefined4 MprCtrlMcmd::CtrlGetStillEdit(int param_1,char **param_2)

{
  int iVar1;
  char *pcVar2;
  int iVar3;
  int iVar4;
  undefined4 *puVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  StillDataInfo aSStack_2c [12];
  
  iVar4 = DAT_000247e4 + 0x24650;
  if (param_1 < 3) {
    puVar5 = *(undefined4 **)(iVar4 + DAT_000247e8);
    MonCtrl::ConPutStr((char *)*puVar5);
    MonCtrl::ConPutStr((char *)*puVar5);
    MonCtrl::ConPutStr((char *)*puVar5);
    MonCtrl::ConPutStr((char *)*puVar5);
    MonCtrl::ConPutStr((char *)*puVar5);
    MonCtrl::ConPutStr((char *)*puVar5);
    return 1;
  }
  iVar1 = StrUtil::StrDecToUInt32(param_2[1]);
  switch(iVar1) {
  case 0:
    if (5 < param_1) {
      iVar4 = StrUtil::StrDecToUInt32(param_2[2]);
      iVar6 = StrUtil::StrDecToUInt32(param_2[3]);
      iVar8 = StrUtil::StrDecToUInt32(param_2[4]);
      pcVar2 = param_2[5];
LAB_00024742:
      iVar3 = StrUtil::StrDecToUInt32(pcVar2);
      iVar7 = 0;
      goto LAB_000247c0;
    }
    puVar5 = *(undefined4 **)(iVar4 + DAT_000247e8);
    MonCtrl::ConPutStr((char *)*puVar5);
    pcVar2 = (char *)*puVar5;
    break;
  case 1:
    if (6 < param_1) {
LAB_00024784:
      iVar7 = StrUtil::StrDecToUInt32(param_2[2]);
      iVar4 = StrUtil::StrDecToUInt32(param_2[3]);
      iVar6 = StrUtil::StrDecToUInt32(param_2[4]);
      iVar8 = StrUtil::StrDecToUInt32(param_2[5]);
      iVar3 = StrUtil::StrDecToUInt32(param_2[6]);
      goto LAB_000247c0;
    }
    puVar5 = *(undefined4 **)(iVar4 + DAT_000247e8);
    MonCtrl::ConPutStr((char *)*puVar5);
    pcVar2 = (char *)*puVar5;
    break;
  case 2:
    if (6 < param_1) {
LAB_00024720:
      iVar4 = StrUtil::StrDecToUInt32(param_2[3]);
      iVar6 = StrUtil::StrDecToUInt32(param_2[4]);
      iVar8 = StrUtil::StrDecToUInt32(param_2[5]);
      pcVar2 = param_2[6];
      goto LAB_00024742;
    }
    puVar5 = *(undefined4 **)(iVar4 + DAT_000247e8);
    MonCtrl::ConPutStr((char *)*puVar5);
    pcVar2 = (char *)*puVar5;
    break;
  case 3:
    if (6 < param_1) goto LAB_00024720;
    puVar5 = *(undefined4 **)(iVar4 + DAT_000247e8);
    MonCtrl::ConPutStr((char *)*puVar5);
    pcVar2 = (char *)*puVar5;
    break;
  case 4:
    if (6 < param_1) goto LAB_00024784;
    puVar5 = *(undefined4 **)(iVar4 + DAT_000247e8);
    MonCtrl::ConPutStr((char *)*puVar5);
    pcVar2 = (char *)*puVar5;
    break;
  default:
    goto switchD_000246a4_default;
  }
  MonCtrl::ConPutStr(pcVar2);
switchD_000246a4_default:
  iVar3 = 0;
  iVar8 = 0;
  iVar6 = 0;
  iVar4 = 0;
  iVar7 = 0;
LAB_000247c0:
  MprCtrl::GetStillDataInfo(iVar1,iVar7,iVar4,iVar6,iVar8,iVar3,aSStack_2c);
  return 1;
}


/* 0002482c */

/* MprCtrlMcmd::CtrlGetStillRec(int, char**) */

undefined4 MprCtrlMcmd::CtrlGetStillRec(int param_1,char **param_2)

{
  int iVar1;
  uint uVar2;
  StillSizeInfo *pSVar3;
  undefined4 uVar4;
  undefined4 *puVar5;
  int iVar6;
  uint local_78 [6];
  undefined4 local_60;
  uint local_5c;
  undefined4 local_58;
  undefined4 local_48;
  undefined4 local_44;
  undefined4 local_40;
  undefined4 local_3c;
  undefined4 local_2c;
  undefined4 local_28;
  undefined4 local_24;
  int local_20 [2];
  
  pSVar3 = (StillSizeInfo *)local_78;
  iVar6 = DAT_00024968 + 0x2483c;
  if (param_1 < 3) {
    puVar5 = *(undefined4 **)(iVar6 + DAT_0002496c);
    MonCtrl::ConPutStr((char *)*puVar5);
    MonCtrl::ConPutStr((char *)*puVar5);
    MonCtrl::ConPutStr((char *)*puVar5);
    MonCtrl::ConPutStr((char *)*puVar5);
    return 1;
  }
  uVar2 = StrUtil::StrDecToUInt32(param_2[1]);
  if (uVar2 == 1) {
    if (param_1 == 3) {
      puVar5 = *(undefined4 **)(iVar6 + DAT_0002496c);
      MonCtrl::ConPutStr((char *)*puVar5);
      MonCtrl::ConPutStr((char *)*puVar5);
      return 0;
    }
    local_5c = uVar2;
    local_58 = StrUtil::StrDecToUInt32(param_2[2]);
    local_48 = StrUtil::StrDecToUInt32(param_2[3]);
    local_44 = StrUtil::StrDecToUInt32(param_2[4]);
    iVar6 = 0x54;
    iVar1 = 0x5c;
    pSVar3 = (StillSizeInfo *)&local_5c;
  }
  else {
    if (uVar2 == 0) {
      if (param_1 == 3) {
        puVar5 = *(undefined4 **)(iVar6 + DAT_0002496c);
        MonCtrl::ConPutStr((char *)*puVar5);
        MonCtrl::ConPutStr((char *)*puVar5);
        return 0;
      }
      local_40 = 0;
      local_3c = StrUtil::StrDecToUInt32(param_2[2]);
      local_2c = StrUtil::StrDecToUInt32(param_2[3]);
      local_28 = StrUtil::StrDecToUInt32(param_2[4]);
      pSVar3 = (StillSizeInfo *)&local_40;
    }
    else {
      if (uVar2 != 2) {
        return 0;
      }
      local_78[0] = uVar2;
      local_78[1] = StrUtil::StrDecToUInt32(param_2[2]);
      local_60 = StrUtil::StrDecToUInt32(param_2[3]);
    }
    iVar6 = 0x5c;
    iVar1 = 0x54;
  }
  local_20[1] = 0;
  local_20[0] = 0;
  local_24 = 0;
  uVar4 = MprCtrl::GetStillRecInfo
                    (pSVar3,(int *)((int)local_78 + iVar6),local_20,(uint *)((int)local_78 + iVar1))
  ;
  return uVar4;
}


/* 00024990 */

/* MprCtrlMcmd::CtrlGetStillSize(int, char**) */

undefined4 MprCtrlMcmd::CtrlGetStillSize(int param_1,char **param_2)

{
  ushort uVar1;
  ushort uVar2;
  undefined4 uVar3;
  StillSize aSStack_14 [4];
  
  if (param_1 < 3) {
    MonCtrl::ConPutStr((char *)**(undefined4 **)(DAT_000249d4 + 0x2499c + DAT_000249d8));
    uVar3 = 1;
  }
  else {
    uVar1 = StrUtil::StrDecToUInt32(param_2[1]);
    uVar2 = StrUtil::StrDecToUInt32(param_2[2]);
    uVar3 = MprCtrl::GetStillSize(uVar1,uVar2,aSStack_14);
  }
  return uVar3;
}


/* 000249e0 */

/* MprCtrlMcmd::CtrlUpmEventTest(int, char**) */

undefined4 MprCtrlMcmd::CtrlUpmEventTest(int param_1,char **param_2)

{
  undefined2 uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int *piVar6;
  void *pvVar7;
  uint uVar8;
  int iVar9;
  undefined4 *puVar10;
  undefined4 local_4c;
  int local_48;
  int local_44;
  uint local_40;
  undefined4 local_3c;
  undefined2 local_38;
  int local_34 [4];
  
  iVar9 = DAT_00024b3c + 150000;
  if (param_1 < 3) {
    puVar10 = *(undefined4 **)(iVar9 + DAT_00024b40);
    MonCtrl::ConPutStr((char *)*puVar10);
    MonCtrl::ConPutStr((char *)*puVar10);
    MonCtrl::ConPutStr((char *)*puVar10);
    MonCtrl::ConPutStr((char *)*puVar10);
    return 1;
  }
  iVar2 = StrUtil::StrDecToUInt32(param_2[1]);
  iVar3 = StrUtil::StrDecToUInt32(param_2[2]);
  if (param_1 == 3) {
    iVar4 = 0;
LAB_00024b30:
    local_4c = 0;
LAB_00024b34:
    uVar1 = 0;
    iVar5 = 0;
  }
  else {
    iVar4 = StrUtil::StrDecToUInt32(param_2[3]);
    if (param_1 == 4) goto LAB_00024b30;
    local_4c = StrUtil::StrDecToUInt32(param_2[4]);
    if (param_1 == 5) goto LAB_00024b34;
    uVar1 = StrUtil::StrDecToUInt32(param_2[5]);
    if (param_1 == 6) {
      iVar5 = 0;
    }
    else {
      iVar5 = StrUtil::StrDecToUInt32(param_2[6]);
    }
  }
  if (iVar2 == 1) {
    local_44 = iVar3;
    if (iVar3 != 1) {
      if (iVar3 == 0) {
        local_44 = 0;
      }
      else if (iVar3 != 2) {
        local_44 = 3;
      }
    }
    local_40 = (uint)(iVar4 != 0);
    if (local_40 == 0) {
      local_3c = local_4c;
    }
    else {
      local_3c = 0;
    }
    iVar2 = 0x14;
    piVar6 = &local_48;
    pvVar7 = (void *)**(undefined4 **)(iVar9 + DAT_00024b54);
    uVar8 = 1;
    local_48 = iVar5;
    local_38 = uVar1;
    goto LAB_00024b1c;
  }
  if (iVar2 == 0) {
    local_34[2] = iVar3;
    if ((iVar3 != 0) && (iVar3 != 1)) {
      local_34[2] = 2;
    }
    piVar6 = local_34 + 2;
    iVar2 = 4;
    pvVar7 = (void *)**(undefined4 **)(iVar9 + DAT_00024b54);
    uVar8 = 0;
    goto LAB_00024b1c;
  }
  if (iVar2 != 2) {
    return 1;
  }
  local_34[0] = 0;
  iVar2 = 1;
  local_34[1] = 1;
  switch(iVar3) {
  case 0:
    goto switchD_00024af8_caseD_0;
  case 1:
    break;
  case 2:
    iVar2 = 2;
    break;
  case 3:
    iVar2 = 4;
    break;
  default:
    iVar2 = -1;
  }
  local_34[0] = iVar2;
switchD_00024af8_caseD_0:
  piVar6 = local_34;
  iVar2 = 8;
  pvVar7 = (void *)**(undefined4 **)(iVar9 + DAT_00024b54);
  uVar8 = 2;
LAB_00024b1c:
  MprCtrlUpmEvent::CallbackPoint(piVar6,iVar2,pvVar7,uVar8);
  return 1;
}


/* 00024b58 */

/* MprCtrlMcmd::ExecSubCmd(int, char**) */

void MprCtrlMcmd::ExecSubCmd(int param_1,char **param_2)

{
  (*(code *)PTR_MonCmdParseSubCmd_0004c1e0)
            (*(undefined4 *)(DAT_00024b74 + 0x24b62 + DAT_00024b78),param_1 + -1,param_2 + 1);
  return;
}


/* 00024b7c */

/* MonLib::ConPutStr(char const*) */

void MonLib::ConPutStr(char *param_1)

{
  (*(code *)PTR_ConPutStr_0004bf4c)(param_1,1);
  return;
}


/* 00024b8c */

/* MprCtrlMcmd::DispInfo(int, char**) */

undefined4 MprCtrlMcmd::DispInfo(int param_1,char **param_2)

{
  uint uVar1;
  int iVar2;
  
  if (param_1 < 2) {
    uVar1 = 1;
  }
  else {
    iVar2 = StrUtil::StrICmp(param_2[1],(char *)(DAT_00024c2c + 0x24ba2));
    if (iVar2 == 0) {
      uVar1 = 0x6f;
    }
    else {
      iVar2 = StrUtil::StrICmp(param_2[1],(char *)(DAT_00024c30 + 0x24bb6));
      if (iVar2 == 0) {
        uVar1 = 1;
      }
      else {
        iVar2 = StrUtil::StrICmp(param_2[1],(char *)(DAT_00024c34 + 0x24bc6));
        if (iVar2 == 0) {
          uVar1 = 2;
        }
        else {
          iVar2 = StrUtil::StrICmp(param_2[1],(char *)(DAT_00024c38 + 0x24bd6));
          if (iVar2 == 0) {
            uVar1 = 4;
          }
          else {
            iVar2 = StrUtil::StrICmp(param_2[1],(char *)(DAT_00024c3c + 0x24be6));
            if (iVar2 == 0) {
              uVar1 = 8;
            }
            else {
              iVar2 = StrUtil::StrICmp(param_2[1],(char *)(DAT_00024c40 + 0x24bf6));
              if (iVar2 == 0) {
                uVar1 = 0x10;
              }
              else {
                iVar2 = StrUtil::StrICmp(param_2[1],(char *)(DAT_00024c44 + 0x24c06));
                if (iVar2 == 0) {
                  uVar1 = 0x20;
                }
                else {
                  iVar2 = StrUtil::StrICmp(param_2[1],(char *)(DAT_00024c48 + 0x24c16));
                  if (iVar2 != 0) {
                    MonLib::ConPutStr((char *)(DAT_00024c4c + 0x24c24));
                    return 1;
                  }
                  uVar1 = 0x40;
                }
              }
            }
          }
        }
      }
    }
  }
  MprCtrl::PrintInfo(uVar1);
  return 1;
}


/* 00024c50 */

/* MprCtrlMcmd::DispVer(int, char**) */

undefined4 MprCtrlMcmd::DispVer(int param_1,char **param_2)

{
  char *pcVar1;
  
  pcVar1 = (char *)(DAT_00024c74 + 0x24c5a);
  MonLib::ConPutStr(pcVar1);
  MonLib::ConPutStr((char *)(DAT_00024c78 + 0x24c64));
  MprCtrl::PrintVersion();
  MonLib::ConPutStr(pcVar1);
  return 1;
}


/* 00024c7c */

/* MprCtrl::CreateDsys(unsigned int) */

void MprCtrl::CreateDsys(uint param_1)

{
                    /* WARNING: Could not recover jumptable at 0x0001ed08. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*(code *)PTR_CreateMMgrExec_0004bd74)(param_1,1);
  return;
}


/* 00024c8c */

/* MprCtrlMcmd::CtrlCreateDsys(int, char**) */

undefined4 MprCtrlMcmd::CtrlCreateDsys(int param_1,char **param_2)

{
  uint uVar1;
  int iVar2;
  undefined4 *puVar3;
  
  puVar3 = *(undefined4 **)(DAT_00024cd0 + 0x24c96 + DAT_00024cd4);
  if (param_1 < 2) {
    MonCtrl::ConPutStr((char *)*puVar3);
  }
  uVar1 = StrUtil::StrHexToUInt32(param_2[1]);
  iVar2 = MprCtrl::CreateDsys(uVar1);
  if (iVar2 == 0) {
    MonCtrl::ConPutStr((char *)*puVar3);
  }
  else {
    MonCtrl::ConPrintf((char *)*puVar3,DAT_00024ce0 + 0x24cca,iVar2);
  }
  return 1;
}


/* 00024ce4 */

/* MprCtrl::DeleteDsys(unsigned int) */

void MprCtrl::DeleteDsys(uint param_1)

{
                    /* WARNING: Could not recover jumptable at 0x0001f3b0. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*(code *)PTR_DeleteMMgrExec_0004bf90)(param_1,1);
  return;
}


/* 00024cf4 */

/* MprCtrlMcmd::CtrlDeleteDsys(int, char**) */

undefined4 MprCtrlMcmd::CtrlDeleteDsys(int param_1,char **param_2)

{
  uint uVar1;
  undefined4 *puVar2;
  
  puVar2 = *(undefined4 **)(DAT_00024d28 + 0x24cfe + DAT_00024d2c);
  if (param_1 < 2) {
    MonCtrl::ConPutStr((char *)*puVar2);
  }
  uVar1 = StrUtil::StrHexToUInt32(param_2[1]);
  MprCtrl::DeleteDsys(uVar1);
  MonCtrl::ConPutStr((char *)*puVar2);
  return 1;
}


/* 00024d38 */

/* MprCtrlMcmd::CtrlCreateMMgr(int, char**) */

undefined4 MprCtrlMcmd::CtrlCreateMMgr(int param_1,char **param_2)

{
  uint uVar1;
  int iVar2;
  undefined4 *puVar3;
  
  puVar3 = *(undefined4 **)(DAT_00024d7c + 0x24d42 + DAT_00024d80);
  if (param_1 < 2) {
    MonCtrl::ConPutStr((char *)*puVar3);
  }
  uVar1 = StrUtil::StrHexToUInt32(param_2[1]);
  iVar2 = MprCtrl::CreateMMgr(uVar1);
  if (iVar2 == 0) {
    MonCtrl::ConPutStr((char *)*puVar3);
  }
  else {
    MonCtrl::ConPrintf((char *)*puVar3,DAT_00024d8c + 0x24d76,iVar2);
  }
  return 1;
}


/* 00024d90 */

/* MprCtrlMcmd::CtrlDeleteMMgr(int, char**) */

undefined4 MprCtrlMcmd::CtrlDeleteMMgr(int param_1,char **param_2)

{
  uint uVar1;
  undefined4 *puVar2;
  
  puVar2 = *(undefined4 **)(DAT_00024dc4 + 0x24d9a + DAT_00024dc8);
  if (param_1 < 2) {
    MonCtrl::ConPutStr((char *)*puVar2);
  }
  uVar1 = StrUtil::StrHexToUInt32(param_2[1]);
  MprCtrl::DeleteMMgr(uVar1);
  MonCtrl::ConPutStr((char *)*puVar2);
  return 1;
}


/* 00024dd4 */

/* MprCtrlMcmd::Init() */

void MprCtrlMcmd::Init(void)

{
  MonCtrl *pMVar1;
  undefined4 uVar2;
  int iVar3;
  
  iVar3 = DAT_00024e60;
  pMVar1 = operator_new(0xc);
  iVar3 = iVar3 + 0x24dea;
  MonCtrl::MonCtrl(pMVar1,(char *)(DAT_00024e64 + 0x24dec),true);
  **(undefined4 **)(iVar3 + DAT_00024e68) = pMVar1;
  pMVar1 = operator_new(0xc);
  MonCtrl::MonCtrl(pMVar1,(char *)(DAT_00024e6c + 0x24e06),true);
  **(undefined4 **)(iVar3 + DAT_00024e70) = pMVar1;
  pMVar1 = operator_new(0xc);
  MonCtrl::MonCtrl(pMVar1,(char *)(DAT_00024e74 + 0x24e1e),false);
  **(undefined4 **)(iVar3 + DAT_00024e78) = pMVar1;
  uVar2 = MonCtrl::GetFlagPtr();
  iVar3 = *(int *)(iVar3 + DAT_00024e7c);
  *(undefined4 *)(iVar3 + 4) = uVar2;
  uVar2 = MonCtrl::GetFlagPtr();
  *(undefined4 *)(iVar3 + 0xc) = uVar2;
  uVar2 = MonCtrl::GetFlagPtr();
  *(undefined4 *)(iVar3 + 0x14) = uVar2;
  return;
}


/* 00024e80 */

/* MprCtrlMcmd::Release() */

void MprCtrlMcmd::Release(void)

{
  int *piVar1;
  int iVar2;
  int *piVar3;
  int *piVar4;
  int *piVar5;
  
  iVar2 = DAT_00024ebc + 0x24e8c;
  piVar5 = *(int **)(iVar2 + DAT_00024ec0);
  piVar1 = (int *)*piVar5;
  if (piVar1 != (int *)0x0) {
    (**(code **)(*piVar1 + 4))();
  }
  piVar4 = *(int **)(iVar2 + DAT_00024ec4);
  piVar1 = (int *)*piVar4;
  if (piVar1 != (int *)0x0) {
    (**(code **)(*piVar1 + 4))();
  }
  piVar3 = *(int **)(iVar2 + DAT_00024ec8);
  piVar1 = (int *)*piVar3;
  if (piVar1 != (int *)0x0) {
    (**(code **)(*piVar1 + 4))();
  }
  *piVar5 = 0;
  *piVar4 = 0;
  *piVar3 = 0;
  return;
}


/* 00024ecc */

/* MprCtrlMcmd::RegisterCommand() */

void MprCtrlMcmd::RegisterCommand(void)

{
  int iVar1;
  char *pcVar2;
  
  iVar1 = DAT_00024ef4 + 0x24eda;
  pcVar2 = (char *)(DAT_00024efc + 0x24ede);
  MonLib::MonCmdAdd(pcVar2,*(_func_bool_int_char_ptr_ptr **)(iVar1 + DAT_00024ef8),
                    (char *)(DAT_00024f00 + 0x24ee4));
  (*(code *)PTR_MonFlgAdd_0004bf04)(pcVar2,*(undefined4 *)(iVar1 + DAT_00024f04));
  return;
}


/* 00024f08 */

/* MprCtrlMcmd::UnregisterCommand() */

void MprCtrlMcmd::UnregisterCommand(void)

{
  char *pcVar1;
  
  pcVar1 = (char *)(DAT_00024f20 + 0x24f12);
  MonLib::MonFlgDel(pcVar1);
  (*(code *)PTR_MonCmdDel_0004c190)(pcVar1);
  return;
}


/* 00024f24 */

/* MprCtrlMcmd::GetMonMsg() */

undefined4 MprCtrlMcmd::GetMonMsg(void)

{
  return **(undefined4 **)(DAT_00024f34 + 0x24f2c + DAT_00024f38);
}


/* 00024f3c */

/* MprCtrlMcmd::GetMonDbg() */

undefined4 MprCtrlMcmd::GetMonDbg(void)

{
  return **(undefined4 **)(DAT_00024f4c + 0x24f44 + DAT_00024f50);
}


/* 00024f54 */

/* MprCtrlMcmd::GetMonErr() */

undefined4 MprCtrlMcmd::GetMonErr(void)

{
  return **(undefined4 **)(DAT_00024f64 + 0x24f5c + DAT_00024f68);
}


/* 00024f6c */

/* MprCtrlInputEvent::~MprCtrlInputEvent() */

void __thiscall MprCtrlInputEvent::~MprCtrlInputEvent(MprCtrlInputEvent *this)

{
  *(int *)this = *(int *)(DAT_00024f80 + 0x24f74 + DAT_00024f84) + 8;
  return;
}


/* 00024f88 */

/* MprCtrlInputEvent::~MprCtrlInputEvent() */

MprCtrlInputEvent * __thiscall MprCtrlInputEvent::~MprCtrlInputEvent(MprCtrlInputEvent *this)

{
  ~MprCtrlInputEvent(this);
  operator_delete(this);
  return this;
}


/* 00024f9c */

/* MprCtrl::GetEventSwitcherInstance() */

undefined4 MprCtrl::GetEventSwitcherInstance(void)

{
  return **(undefined4 **)(DAT_00024fac + 0x24fa4 + DAT_00024fb0);
}


/* 00024fb4 */

/* MprCtrlInputEvent::MprCtrlInputEvent() */

void __thiscall MprCtrlInputEvent::MprCtrlInputEvent(MprCtrlInputEvent *this)

{
  *(int *)this = *(int *)(DAT_00024fc8 + 0x24fbc + DAT_00024fcc) + 8;
  return;
}


/* 00024fd0 */

/* MprCtrlInputEvent::ResetEvent() */

void __thiscall MprCtrlInputEvent::ResetEvent(MprCtrlInputEvent *this)

{
  this[4] = (MprCtrlInputEvent)0x1;
  this[5] = (MprCtrlInputEvent)0x0;
  this[7] = (MprCtrlInputEvent)0x0;
  this[8] = (MprCtrlInputEvent)0x0;
  this[9] = (MprCtrlInputEvent)0x0;
  return;
}


/* 00024fe4 */

/* MprCtrlInputEvent::Clear(unsigned int) */

void __thiscall MprCtrlInputEvent::Clear(MprCtrlInputEvent *this,uint param_1)

{
  EventSwitcher *this_00;
  
  if ((*(uint *)(this + 0xc) != param_1) && (param_1 != 0)) {
    return;
  }
  this_00 = (EventSwitcher *)MprCtrl::GetEventSwitcherInstance();
  EventSwitcher::DeleteInstance(this_00,this);
  (*(code *)PTR_ResetEvent_0004bc90)(this);
  return;
}


/* 00025008 */

/* MprCtrlInputEvent::Init(unsigned int) */

void __thiscall MprCtrlInputEvent::Init(MprCtrlInputEvent *this,uint param_1)

{
  undefined4 uVar1;
  EventSwitcher *this_00;
  int iVar2;
  uint local_38;
  undefined4 local_34;
  undefined4 local_30;
  MprCtrlInputEvent *local_2c;
  uint local_28;
  undefined4 local_24;
  undefined4 local_20;
  MprCtrlInputEvent *local_1c;
  
  Clear(this,0);
  uVar1 = MprCtrlMcmd::GetMonMsg();
  iVar2 = DAT_00025088 + 0x25024;
  *(undefined4 *)(this + 0x10) = uVar1;
  uVar1 = MprCtrlMcmd::GetMonErr();
  *(undefined4 *)(this + 0x14) = uVar1;
  uVar1 = MprCtrlMcmd::GetMonDbg();
  *(uint *)(this + 0xc) = param_1;
  *(undefined4 *)(this + 0x18) = uVar1;
  this_00 = (EventSwitcher *)MprCtrl::GetEventSwitcherInstance();
  ResetEvent(this);
  memset(&local_38,0,0x20);
  local_34 = DAT_00025080;
  local_30 = *(undefined4 *)(iVar2 + DAT_0002508c);
  local_24 = DAT_00025084;
  local_38 = param_1;
  local_2c = this;
  local_28 = param_1;
  local_20 = local_30;
  local_1c = this;
  EventSwitcher::AddInstance(this_00,this);
  EventSwitcher::AddCallbackFunc(this_00,this,2,(_CallbackEntry *)&local_38);
  return;
}


/* 00025090 */

/* MprCtrlInputEvent::SendInputEvent(int, int) */

void __thiscall MprCtrlInputEvent::SendInputEvent(MprCtrlInputEvent *this,int param_1,int param_2)

{
  int iVar1;
  int iVar2;
  int *local_1c [2];
  
  iVar1 = osal_valloc_msg_wait(DAT_000250f8,local_1c,0x10,1);
  iVar2 = DAT_00025104;
  if (iVar1 == 0) {
    local_1c[0][1] = 0;
    local_1c[0][3] = 0;
    *local_1c[0] = param_1;
    local_1c[0][2] = param_2;
    MonCtrl::ConPrintfMessage(*(char **)(this + 0x18),iVar2 + 0x250c4,param_1,param_2);
    iVar2 = osal_snd_msg(DAT_000250f8,local_1c[0]);
    if (iVar2 != 0) {
      MonCtrl::ConPrintfMessage(*(char **)(this + 0x14),DAT_00025108 + 0x250e4,iVar2);
      osal_free_msg(DAT_000250fc,local_1c[0]);
    }
  }
  else {
    MonCtrl::ConPrintfMessage(*(char **)(this + 0x14),DAT_00025100 + 0x250b4,iVar1);
  }
  return;
}


/* 0002510c */

/* MprCtrlInputEvent::CallbackPoint(unsigned int, unsigned int, void*, unsigned int, void*) */

uint MprCtrlInputEvent::CallbackPoint
               (uint param_1,uint param_2,void *param_3,uint param_4,void *param_5)

{
  char cVar1;
  byte bVar2;
  int iVar3;
  uint uVar4;
  
  iVar3 = DAT_000251a4;
  cVar1 = *(char *)((int)param_5 + 4);
  if (param_2 == DAT_0002519c) {
    uVar4 = (*(code *)PTR_ResetEvent_0004bc90)(param_5);
    return uVar4;
  }
  if (param_2 != DAT_000251a0) {
    return param_1;
  }
  if ((cVar1 == '\0') && (*(char *)((int)param_5 + 5) == *(char *)param_3)) {
LAB_00025146:
    if (*(char *)((int)param_5 + 6) == *(char *)((int)param_3 + 4)) goto LAB_0002515a;
  }
  else {
    bVar2 = *(byte *)param_3;
    *(byte *)((int)param_5 + 5) = bVar2;
    param_1 = SendInputEvent(param_5,iVar3,(uint)bVar2);
    if (cVar1 == '\0') goto LAB_00025146;
  }
  iVar3 = DAT_000251a8;
  bVar2 = *(byte *)((int)param_3 + 4);
  *(byte *)((int)param_5 + 6) = bVar2;
  param_1 = SendInputEvent(param_5,iVar3,(uint)bVar2);
LAB_0002515a:
  bVar2 = *(byte *)((int)param_3 + 1);
  if ((uint)*(byte *)((int)param_5 + 7) != (uint)bVar2) {
    *(byte *)((int)param_5 + 7) = bVar2;
    param_1 = SendInputEvent(param_5,0xd000000,(uint)bVar2);
  }
  bVar2 = *(byte *)((int)param_3 + 3);
  if ((uint)*(byte *)((int)param_5 + 9) != (uint)bVar2) {
    *(byte *)((int)param_5 + 9) = bVar2;
    param_1 = SendInputEvent(param_5,DAT_000251ac,(uint)bVar2);
  }
  if (*(char *)((int)param_5 + 8) == *(char *)((int)param_3 + 2)) {
    return param_1;
  }
  *(char *)((int)param_5 + 8) = *(char *)((int)param_3 + 2);
  uVar4 = (*(code *)PTR_SendInputEvent_0004c260)(param_5,DAT_000251b0);
  return uVar4;
}


/* 000251b4 */

/* MprCtrlUpmEvent::CallbackFuncRsrcLIFO(void*, MWF::ObjMsg, DefRsrc::AcsrId_t) */

void MprCtrlUpmEvent::CallbackFuncRsrcLIFO(int param_1)

{
  (*(code *)PTR_ConPrintfMessage_0004c114)(*(undefined4 *)(param_1 + 0x30),DAT_000251c8 + 0x251bc);
  return;
}


/* 000251cc */

/* MprCtrlUpmEvent::rsrcInfo::Init() */

void __thiscall MprCtrlUpmEvent::rsrcInfo::Init(rsrcInfo *this)

{
  *(undefined4 *)this = 0;
  return;
}


/* 000251d6 */

/* MprCtrlUpmEvent::rsrcInfo::ChangeStat(MprCtrlUpmEvent::AcquiredStat) */

void __thiscall MprCtrlUpmEvent::rsrcInfo::ChangeStat(rsrcInfo *this,undefined4 param_2)

{
  *(undefined4 *)this = param_2;
  return;
}


/* 000251e0 */

/* MprCtrlUpmEvent::CallbackFuncRsrcAcvPwr(void*, MWF::ObjMsg) */

void MprCtrlUpmEvent::CallbackFuncRsrcAcvPwr(int param_1)

{
  int iVar1;
  
  MonCtrl::ConPrintfMessage(*(char **)(param_1 + 0x30),DAT_00025210 + 0x251e8);
  rsrcInfo::ChangeStat((rsrcInfo *)(param_1 + 0x24),2);
  iVar1 = DAT_00025214;
  *(uint *)(param_1 + 4) = *(uint *)(param_1 + 4) | 2;
  (*(code *)PTR_ConPrintfMessage_0004c114)(*(undefined4 *)(param_1 + 0x30),iVar1 + 0x2520a);
  return;
}


/* 00025218 */

/* MprCtrlUpmEvent::CallbackFuncRsrcBodyTmp(void*, MWF::ObjMsg) */

void MprCtrlUpmEvent::CallbackFuncRsrcBodyTmp(int param_1)

{
  int iVar1;
  
  MonCtrl::ConPrintfMessage(*(char **)(param_1 + 0x30),DAT_00025248 + 0x25220);
  rsrcInfo::ChangeStat((rsrcInfo *)(param_1 + 0x20),2);
  iVar1 = DAT_0002524c;
  *(uint *)(param_1 + 4) = *(uint *)(param_1 + 4) | 1;
  (*(code *)PTR_ConPrintfMessage_0004c114)(*(undefined4 *)(param_1 + 0x30),iVar1 + 0x25242);
  return;
}


/* 00025250 */

/* MprCtrlUpmEvent::RegenarateResourseAcsr(unsigned int) */

void __thiscall MprCtrlUpmEvent::RegenarateResourseAcsr(MprCtrlUpmEvent *this,uint param_1)

{
  RsrcAcsr *pRVar1;
  int iVar2;
  
  iVar2 = DAT_000252e0;
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x30),DAT_000252dc + 0x25264,param_1);
  iVar2 = iVar2 + 0x2526e;
  if (param_1 == 1) {
    if (*(int **)(this + 0x18) != (int *)0x0) {
      (**(code **)(**(int **)(this + 0x18) + 4))();
      pRVar1 = operator_new(0x28);
      MWF::RsrcAcsr::RsrcAcsr
                (pRVar1,0x5d,this,*(undefined4 *)(iVar2 + DAT_000252e8),
                 *(undefined4 *)(iVar2 + DAT_000252e4));
      *(RsrcAcsr **)(this + 0x18) = pRVar1;
    }
  }
  else if ((param_1 == 2) && (*(int **)(this + 0x1c) != (int *)0x0)) {
    (**(code **)(**(int **)(this + 0x1c) + 4))();
    pRVar1 = operator_new(0x28);
    MWF::RsrcAcsr::RsrcAcsr
              (pRVar1,0x5f,this,*(undefined4 *)(iVar2 + DAT_000252ec),
               *(undefined4 *)(iVar2 + DAT_000252e4));
    *(RsrcAcsr **)(this + 0x1c) = pRVar1;
  }
  return;
}


/* 000252f0 */

/* MprCtrlUpmEvent::UpdateResourse(unsigned int, bool) */

void __thiscall MprCtrlUpmEvent::UpdateResourse(MprCtrlUpmEvent *this,uint param_1,bool param_2)

{
  int iVar1;
  char *pcVar2;
  uint uVar3;
  uint uVar4;
  rsrcInfo *prVar5;
  undefined1 auStack_28 [12];
  
  uVar3 = (uint)param_2;
  MWF::ObjMsg::ObjMsg(auStack_28);
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x30),DAT_000254e8 + 0x2530e,param_1,uVar3);
  if ((param_1 & 2) != 0) {
    uVar4 = *(uint *)(this + 4);
    if (uVar3 == 0) {
      if ((uVar4 & 2) == 0) {
        if (*(int *)(this + 0x24) == 1) {
          RegenarateResourseAcsr(this,2);
          rsrcInfo::ChangeStat((rsrcInfo *)(this + 0x24),0);
        }
      }
      else {
        *(uint *)(this + 4) = uVar4 & 0xfffffffd;
        if (*(int *)(this + 0x24) == 2) {
          MonCtrl::ConPrintfMessage(*(char **)(this + 0x30),DAT_00025500 + 0x253b2);
          rsrcInfo::ChangeStat((rsrcInfo *)(this + 0x24),0);
          iVar1 = MWF::RsrcAcsr::Release();
          if (iVar1 == 0) {
            pcVar2 = *(char **)(this + 0x30);
            iVar1 = DAT_00025504 + 0x253ce;
          }
          else {
            pcVar2 = *(char **)(this + 0x2c);
            iVar1 = DAT_00025508 + 0x253d6;
          }
          goto LAB_000253d4;
        }
      }
    }
    else if (((uVar4 & 2) == 0) && ((*(int *)(this + 0x24) == 0 || (*(int *)(this + 0x24) == 3)))) {
      prVar5 = (rsrcInfo *)(this + 0x24);
      rsrcInfo::ChangeStat(prVar5,1);
      iVar1 = MWF::RsrcAcsr::Acquire(*(undefined4 *)(this + 0x1c),auStack_28,1);
      MonCtrl::ConPrintfMessage(*(char **)(this + 0x2c),DAT_000254ec + 0x2534e);
      if (iVar1 == 0) {
        rsrcInfo::ChangeStat(prVar5,2);
        iVar1 = DAT_000254f0;
        pcVar2 = *(char **)(this + 0x30);
        *(uint *)(this + 4) = *(uint *)(this + 4) | 2;
        iVar1 = iVar1 + 0x2536a;
      }
      else if (iVar1 == 0x9000) {
        pcVar2 = *(char **)(this + 0x2c);
        iVar1 = DAT_000254f4 + 0x25378;
      }
      else if (iVar1 == 0x9001) {
        pcVar2 = *(char **)(this + 0x2c);
        iVar1 = DAT_000254f8 + 0x25388;
      }
      else {
        rsrcInfo::ChangeStat(prVar5,3);
        pcVar2 = *(char **)(this + 0x2c);
        iVar1 = DAT_000254fc + 0x25398;
      }
LAB_000253d4:
      MonCtrl::ConPrintfMessage(pcVar2,iVar1);
    }
  }
  if ((param_1 & 1) == 0) goto LAB_000254cc;
  uVar4 = *(uint *)(this + 4);
  if (uVar3 == 0) {
    if ((uVar4 & 1) == 0) {
      if (*(int *)(this + 0x20) == 1) {
        RegenarateResourseAcsr(this,1);
        rsrcInfo::ChangeStat((rsrcInfo *)(this + 0x24),0);
      }
      goto LAB_000254cc;
    }
    *(uint *)(this + 4) = uVar4 & 0xfffffffe;
    if (*(int *)(this + 0x20) != 2) goto LAB_000254cc;
    MonCtrl::ConPrintfMessage(*(char **)(this + 0x30),DAT_00025520 + 0x25490);
    rsrcInfo::ChangeStat((rsrcInfo *)(this + 0x20),0);
    iVar1 = MWF::RsrcAcsr::Release();
    if (iVar1 == 0) {
      pcVar2 = *(char **)(this + 0x30);
      iVar1 = DAT_00025524 + 0x254ac;
    }
    else {
      pcVar2 = *(char **)(this + 0x2c);
      iVar1 = DAT_00025528 + 0x254b4;
    }
  }
  else {
    if (((uVar4 & 1) != 0) || ((*(int *)(this + 0x20) != 0 && (*(int *)(this + 0x20) != 3))))
    goto LAB_000254cc;
    prVar5 = (rsrcInfo *)(this + 0x20);
    rsrcInfo::ChangeStat(prVar5,1);
    iVar1 = MWF::RsrcAcsr::Acquire(*(undefined4 *)(this + 0x18),auStack_28,1);
    MonCtrl::ConPrintfMessage(*(char **)(this + 0x2c),DAT_0002550c + 0x2542c);
    if (iVar1 == 0) {
      rsrcInfo::ChangeStat(prVar5,2);
      iVar1 = DAT_00025510;
      pcVar2 = *(char **)(this + 0x2c);
      *(uint *)(this + 4) = *(uint *)(this + 4) | 1;
      iVar1 = iVar1 + 0x25448;
    }
    else if (iVar1 == 0x9000) {
      pcVar2 = *(char **)(this + 0x2c);
      iVar1 = DAT_00025514 + 0x25456;
    }
    else if (iVar1 == 0x9001) {
      pcVar2 = *(char **)(this + 0x2c);
      iVar1 = DAT_00025518 + 0x25466;
    }
    else {
      rsrcInfo::ChangeStat(prVar5,3);
      pcVar2 = *(char **)(this + 0x2c);
      iVar1 = DAT_0002551c + 0x25476;
    }
  }
  MonCtrl::ConPrintfMessage(pcVar2,iVar1);
LAB_000254cc:
  MWF::ObjMsg::~ObjMsg(auStack_28);
  return;
}


/* 0002552c */

/* MprCtrlUpmEvent::UpdateInhInfo(MprCtrlUpmEvent::InhFactorId, bool) */

void __thiscall MprCtrlUpmEvent::UpdateInhInfo(MprCtrlUpmEvent *this,int param_2,undefined4 param_3)

{
  int iVar1;
  uint uVar2;
  uint *puVar3;
  uint auStack_3c [5];
  uint local_28;
  uint local_24 [2];
  
  MprCtrlLog::SetParamLog(0xc5,0,(ushort)param_2,(ushort)param_3,0x37f);
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x30),DAT_00025624 + 0x25556,param_2,param_2,param_3);
  if (param_2 - 1U < 3) {
    iVar1 = *(int *)(DAT_00025628 + 0x25568 + (param_2 - 1U) * 4);
    if (iVar1 == 0) goto LAB_00025582;
  }
  else {
    iVar1 = 0x17;
  }
  MWF::InhMgr::ChangeInhFactorStatus(*(undefined4 *)(this + 0xc),iVar1,param_3);
  MWF::InhMgr::UpdateInhFactor();
  if (param_2 != 0) {
    return;
  }
LAB_00025582:
  local_24[0] = 0;
  MprCtrl::GetMediaIdList(5,auStack_3c,local_24);
  if (param_2 == 0) {
    puVar3 = auStack_3c;
    for (uVar2 = 0; uVar2 < local_24[0]; uVar2 = uVar2 + 1) {
      iVar1 = MediaConfigWrapper::GetDeviceType(*puVar3);
      if ((iVar1 == 7) || (iVar1 == 8)) {
        local_28 = 0;
        MediaConfigWrapper::GetRsrcInhOffset(*puVar3,&local_28);
        MWF::InhMgr::ChangeInhFactorStatus(*(undefined4 *)(this + 0xc),local_28 + 0x535,param_3);
      }
      puVar3 = puVar3 + 1;
    }
    puVar3 = auStack_3c;
    for (uVar2 = 0; uVar2 < local_24[0]; uVar2 = uVar2 + 1) {
      iVar1 = MediaConfigWrapper::GetDeviceType(*puVar3);
      if (iVar1 != 6) {
        local_28 = 0;
        MediaConfigWrapper::GetRsrcInhOffset(*puVar3,&local_28);
        MWF::InhMgr::ChangeInhFactorStatus(*(undefined4 *)(this + 0xc),local_28 + 0x54d,param_3);
      }
      puVar3 = puVar3 + 1;
    }
    MWF::InhMgr::UpdateInhFactor();
  }
  return;
}


/* 0002562c */

/* MprCtrlUpmEvent::UpdateMediaInhInfo() */

void __thiscall MprCtrlUpmEvent::UpdateMediaInhInfo(MprCtrlUpmEvent *this)

{
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x30),DAT_00025654 + 0x2563a);
  UpdateInhInfo(this,0,*this);
  (*(code *)PTR_ConPrintfMessage_0004c114)(*(undefined4 *)(this + 0x30),DAT_00025658 + 0x2564e);
  return;
}


/* 0002565c */

/* MprCtrlUpmEvent::CallbackPointBusPower(void*, int, void*, unsigned int) */

void MprCtrlUpmEvent::CallbackPointBusPower(void *param_1,int param_2,void *param_3,uint param_4)

{
  int *piVar1;
  int iVar2;
  char *pcVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  int iVar7;
  
  uVar6 = *(undefined4 *)param_1;
  MonCtrl::ConPrintfMessage(*(char **)((int)param_3 + 0x30),DAT_000257e8 + 0x2566c,param_4);
  iVar2 = MWF::ObjMsg::GetCategoryId();
  if (iVar2 != 0x6107) {
    uVar5 = *(undefined4 *)((int)param_3 + 0x2c);
    uVar6 = MWF::ObjMsg::GetCategoryId();
    (*(code *)PTR_ConPrintfMessage_0004c114)(uVar5,DAT_000257ec + 0x25692,uVar6,0x265);
    return;
  }
  MWF::ObjLock::Lock(*(ObjLock **)((int)param_3 + 0x34));
  iVar2 = MWF::ObjMsg::GetMessageId();
  if (iVar2 == DAT_000257e4) {
    MonCtrl::ConPrintfMessage(*(char **)((int)param_3 + 0x30),DAT_000257f0 + 0x256be);
    iVar2 = MWF::ObjMsg::GetParam(uVar6,0x1005,7);
    if (iVar2 == 0) {
      uVar6 = 0x275;
      pcVar3 = *(char **)((int)param_3 + 0x2c);
      iVar2 = DAT_000257f4 + 0x256da;
    }
    else {
      iVar2 = *(int *)((int)param_3 + 0x40);
      uVar5 = MWF::ParamStd_Template<int,(MWF::Param::Type)7>::GetValue();
      *(undefined4 *)(iVar2 + 0x6c) = uVar5;
      iVar2 = MWF::ObjMsg::GetParam(uVar6,0x100e,7);
      if (iVar2 != 0) {
        iVar7 = *(int *)((int)param_3 + 0x40);
        uVar6 = MWF::ParamStd_Template<int,(MWF::Param::Type)7>::GetValue();
        iVar2 = DAT_000257fc + 0x2570c;
        *(undefined4 *)(iVar7 + 0x70) = uVar6;
        MonCtrl::ConPrintfMessage(*(char **)((int)param_3 + 0x30),iVar2);
        MonCtrl::ConPrintfMessage(*(char **)((int)param_3 + 0x30),DAT_00025800 + 0x2571a);
        MonCtrl::ConPrintfMessage
                  (*(char **)((int)param_3 + 0x30),DAT_00025804 + 0x25728,
                   *(undefined4 *)(*(int *)((int)param_3 + 0x40) + 0x6c));
        MonCtrl::ConPrintfMessage
                  (*(char **)((int)param_3 + 0x30),DAT_00025808 + 0x25736,
                   *(undefined4 *)(*(int *)((int)param_3 + 0x40) + 0x70));
        MprCtrlLog::SetParamLog
                  (0xc6,0,*(ushort *)(*(int *)((int)param_3 + 0x40) + 0x6c),
                   *(ushort *)(*(int *)((int)param_3 + 0x40) + 0x70),0x28b);
        iVar2 = **(int **)((int)param_3 + 0x40);
        if ((iVar2 == 0) || ((*(int **)((int)param_3 + 0x40))[0x1c] == 2)) {
          uVar5 = 0;
          UpdateResourse(param_3,2,false);
          UpdateInhInfo(param_3,1,0);
          *(undefined1 *)param_3 = 0;
          uVar4 = 0;
          uVar6 = 0;
        }
        else {
          if (iVar2 != 1) goto LAB_0001f8c0;
          UpdateResourse(param_3,2,true);
          *(undefined1 *)param_3 = 1;
          UpdateInhInfo(param_3,0,1);
          iVar7 = *(int *)((int)param_3 + 0x40);
          iVar2 = 0;
          piVar1 = (int *)(iVar7 + 4);
          uVar6 = 1;
          uVar5 = 1;
          while (iVar2 != *piVar1) {
            if ((*(uint *)(iVar7 + 0xc) < 2) && (*(short *)(iVar7 + 0x18) != 0)) {
              uVar6 = 0;
            }
            pcVar3 = (char *)(iVar7 + 0x20);
            iVar2 = iVar2 + 1;
            iVar7 = iVar7 + 0x1c;
            if (*pcVar3 != '\0') {
              uVar5 = 0;
            }
          }
          uVar4 = 1;
        }
        UpdateInhInfo(param_3,uVar4,uVar6);
        UpdateInhInfo(param_3,3,uVar5);
        goto LAB_0001f8c0;
      }
      uVar6 = 0x27d;
      pcVar3 = *(char **)((int)param_3 + 0x2c);
      iVar2 = DAT_000257f8 + 0x256fc;
    }
    MonCtrl::ConPrintfMessage(pcVar3,iVar2,uVar6);
  }
LAB_0001f8c0:
  (*(code *)PTR_Unlock_0004c134)(*(undefined4 *)((int)param_3 + 0x34));
  return;
}


/* 0002580c */

/* MprCtrlUpmEvent::CallbackPoint(void*, int, void*, unsigned int) */

void MprCtrlUpmEvent::CallbackPoint(void *param_1,int param_2,void *param_3,uint param_4)

{
  int *piVar1;
  int *piVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  int *piVar6;
  int iVar7;
  uint uVar8;
  int iVar9;
  uint uVar10;
  int iVar11;
  
  MonCtrl::ConPrintfMessage(*(char **)((int)param_3 + 0x30),DAT_00025a84 + 0x2581c,param_4);
  MWF::ObjLock::Lock(*(ObjLock **)((int)param_3 + 0x34));
  if (param_4 == 1) {
    MonCtrl::ConPrintfMessage(*(char **)((int)param_3 + 0x30),DAT_00025a8c + 0x258a8);
    MonCtrl::ConPrintfMessage(*(char **)((int)param_3 + 0x30),DAT_00025a90 + 0x258b2);
    MonCtrl::ConPrintfMessage(*(char **)((int)param_3 + 0x30),DAT_00025a94 + 0x258bc);
    MonCtrl::ConPrintfMessage
              (*(char **)((int)param_3 + 0x30),DAT_00025a98 + 0x258c6,
               *(undefined4 *)((int)param_1 + 8));
    MonCtrl::ConPrintfMessage
              (*(char **)((int)param_3 + 0x30),DAT_00025a9c + 0x258d2,*(undefined4 *)param_1);
    MonCtrl::ConPrintfMessage
              (*(char **)((int)param_3 + 0x30),DAT_00025aa0 + 0x258de,
               *(undefined4 *)((int)param_1 + 4));
    MonCtrl::ConPrintfMessage
              (*(char **)((int)param_3 + 0x30),DAT_00025aa4 + 0x258ea,
               (uint)*(ushort *)((int)param_1 + 0x10));
    MonCtrl::ConPrintfMessage
              (*(char **)((int)param_3 + 0x30),DAT_00025aa8 + 0x258f6,
               *(undefined4 *)((int)param_1 + 0xc));
    MonCtrl::ConPrintfMessage
              (*(char **)((int)param_3 + 0x30),DAT_00025aac + 0x25906,
               *(undefined4 *)(*(int *)((int)param_3 + 0x40) + 4));
    MprCtrlLog::SetParamLog
              (0xc3,*(ushort *)param_1,*(ushort *)((int)param_1 + 4),
               *(ushort *)((int)param_1 + 0x10),0x1ae);
    iVar5 = *(int *)((int)param_3 + 0x40);
    uVar8 = *(uint *)(iVar5 + 4);
    for (uVar10 = 0; uVar10 < uVar8; uVar10 = uVar10 + 1) {
      piVar6 = (int *)(iVar5 + 8);
      iVar5 = iVar5 + 0x1c;
      if (*(int *)param_1 == *piVar6) {
        MonCtrl::ConPrintfMessage(*(char **)((int)param_3 + 0x30),DAT_00025ab0 + 0x25932);
        iVar5 = uVar10 * 0x1c + *(int *)((int)param_3 + 0x40);
        *(undefined4 *)(iVar5 + 0xc) = *(undefined4 *)((int)param_1 + 4);
        *(undefined4 *)(iVar5 + 0x10) = *(undefined4 *)((int)param_1 + 8);
        *(undefined4 *)(iVar5 + 0x14) = *(undefined4 *)((int)param_1 + 0xc);
        *(undefined2 *)(iVar5 + 0x18) = *(undefined2 *)((int)param_1 + 0x10);
        *(undefined1 *)(iVar5 + 0x20) = *(undefined1 *)((int)param_1 + 0x12);
        goto LAB_00025992;
      }
    }
    if (uVar8 < 3) {
      MonCtrl::ConPrintfMessage(*(char **)((int)param_3 + 0x30),DAT_00025ab4 + 0x25968,uVar8);
      iVar5 = *(int *)((int)param_3 + 0x40);
      iVar7 = uVar8 * 0x1c + iVar5;
      *(undefined4 *)(iVar7 + 8) = *(undefined4 *)param_1;
      *(undefined4 *)(iVar7 + 0xc) = *(undefined4 *)((int)param_1 + 4);
      *(undefined4 *)(iVar7 + 0x10) = *(undefined4 *)((int)param_1 + 8);
      *(undefined4 *)(iVar7 + 0x14) = *(undefined4 *)((int)param_1 + 0xc);
      *(undefined2 *)(iVar7 + 0x18) = *(undefined2 *)((int)param_1 + 0x10);
      *(undefined1 *)(iVar7 + 0x20) = *(undefined1 *)((int)param_1 + 0x12);
      *(int *)(iVar5 + 4) = *(int *)(iVar5 + 4) + 1;
    }
LAB_00025992:
    piVar6 = *(int **)((int)param_3 + 0x40);
    iVar7 = *piVar6;
    iVar5 = iVar7;
    if (iVar7 != 0) {
      if (piVar6[0x1c] == 2) {
        iVar7 = 0;
        iVar5 = iVar7;
      }
      else {
        if (iVar7 != 1) goto LAB_0001f8c0;
        piVar2 = piVar6 + 1;
        iVar9 = 0;
        while (iVar9 != *piVar2) {
          if (((uint)piVar6[3] < 2) && ((short)piVar6[6] != 0)) {
            iVar7 = 0;
          }
          piVar1 = piVar6 + 8;
          iVar9 = iVar9 + 1;
          piVar6 = piVar6 + 7;
          if ((char)*piVar1 != '\0') {
            iVar5 = 0;
          }
        }
      }
    }
    UpdateInhInfo(param_3,1,iVar7);
    uVar4 = 3;
  }
  else if (param_4 == 0) {
    MonCtrl::ConPrintfMessage
              (*(char **)((int)param_3 + 0x30),DAT_00025a88 + 0x25844,*(undefined4 *)param_1);
    MprCtrlLog::SetParamLog(0xc2,0,0,*(ushort *)param_1,0x173);
    piVar6 = *(int **)((int)param_3 + 0x40);
    iVar5 = *(int *)param_1;
    *piVar6 = iVar5;
    if ((iVar5 == 0) || (piVar6[0x1c] == 2)) {
      UpdateResourse(param_3,2,false);
      UpdateInhInfo(param_3,1,0);
      uVar4 = 0;
      *(undefined1 *)param_3 = 0;
      iVar5 = 0;
    }
    else {
      if (iVar5 != 1) goto LAB_0001f8c0;
      UpdateResourse(param_3,2,true);
      *(undefined1 *)param_3 = 1;
      uVar4 = 0;
      iVar5 = 1;
    }
  }
  else {
    if (param_4 != 2) {
      MonCtrl::ConPrintfMessage(*(char **)((int)param_3 + 0x2c),DAT_00025abc + 0x25a70);
      goto LAB_0001f8c0;
    }
    MonCtrl::ConPrintfMessage(*(char **)((int)param_3 + 0x30),DAT_00025ab8 + 0x259ec);
    iVar5 = *(int *)((int)param_1 + 4);
    iVar7 = *(int *)((int)param_3 + 0x40);
    iVar11 = *(int *)(iVar7 + 0x68);
    iVar9 = *(int *)(iVar7 + 0x60);
    if (iVar5 == 1) {
      *(undefined4 *)(iVar7 + 0x68) = *(undefined4 *)param_1;
    }
    else {
      if (iVar5 != 0) goto LAB_0001f8c0;
      *(undefined4 *)(iVar7 + 0x60) = *(undefined4 *)param_1;
    }
    iVar3 = *(int *)(iVar7 + 0x68);
    if ((((iVar3 == 2) || (iVar3 == 4)) || (*(int *)(iVar7 + 0x60) == 2)) ||
       (*(int *)(iVar7 + 0x60) == 4)) {
      if (*(int *)param_1 == 1) {
        if (iVar5 == 1) {
          if (((iVar11 != 2) || (*(int *)(iVar7 + 0x60) == 2)) || (*(int *)(iVar7 + 0x60) == 4))
          goto LAB_0001f8c0;
          goto LAB_00025a52;
        }
        if (((iVar5 != 0) || (iVar9 != 2)) || ((iVar3 == 2 || (iVar3 == 4)))) goto LAB_0001f8c0;
        iVar5 = 0;
      }
      else {
        if (*(int *)param_1 != 2) goto LAB_0001f8c0;
        iVar5 = 1;
      }
    }
    else {
LAB_00025a52:
      iVar5 = 0;
    }
    UpdateResourse(param_3,1,SUB41(iVar5,0));
    uVar4 = 2;
  }
  UpdateInhInfo(param_3,uVar4,iVar5);
LAB_0001f8c0:
  (*(code *)PTR_Unlock_0004c134)(*(undefined4 *)((int)param_3 + 0x34));
  return;
}


/* 00025ac0 */

/* MprCtrlUpmEvent::RegisterBusPowerEvent() */

void __thiscall MprCtrlUpmEvent::RegisterBusPowerEvent(MprCtrlUpmEvent *this)

{
  int iVar1;
  char *pcVar2;
  int iVar3;
  undefined4 uVar4;
  ParamStd_Template<unsigned_int,(MWF::Param::Type)8> aPStack_30 [8];
  undefined1 auStack_28 [8];
  undefined1 auStack_20 [8];
  undefined1 *local_18;
  undefined1 *local_14;
  
  MWF::ObjMsg::ObjMsg(auStack_20,0x6107,0x1003);
  MWF::ObjMsg::ObjMsg(auStack_28);
  MemUtil::MemSet8(&local_18,'\0',8);
  MWF::ParamStd_Template<unsigned_int,(MWF::Param::Type)8>::ParamStd_Template((uint)aPStack_30);
  MWF::ObjMsg::AddParam((uint)auStack_20,(Param *)0x1016);
  MWF::ParamStd_Template<unsigned_int,(MWF::Param::Type)8>::~ParamStd_Template(aPStack_30);
  local_14 = auStack_28;
  uVar4 = 0;
  local_18 = auStack_20;
  iVar1 = MWF::EventWrapper::SendAndRecv(*(void **)(this + 0x38),(int)&local_18,(void *)0x8,0);
  if (iVar1 == 0) {
    iVar1 = MWF::ObjMsg::GetMessageId();
    if (iVar1 == DAT_00025bc4) {
      iVar1 = MWF::ObjMsg::GetParam(auStack_28,0x1000,7,DAT_00025bc4,uVar4);
      if (iVar1 == 0) {
        MonCtrl::ConPrintfMessage(*(char **)(this + 0x2c),DAT_00025bd0 + 0x25b72,0x40e);
        goto LAB_00025b8c;
      }
      iVar1 = MWF::ParamStd_Template<int,(MWF::Param::Type)7>::GetValue();
      if (iVar1 == 0) goto LAB_00025b8c;
      uVar4 = 0x415;
      pcVar2 = *(char **)(this + 0x2c);
      iVar3 = DAT_00025bd4 + 0x25b8a;
    }
    else {
      pcVar2 = *(char **)(this + 0x2c);
      iVar1 = MWF::ObjMsg::GetMessageId();
      uVar4 = 0x406;
      iVar3 = DAT_00025bcc + 0x25b56;
    }
  }
  else {
    uVar4 = 0x400;
    pcVar2 = *(char **)(this + 0x2c);
    iVar3 = DAT_00025bc8 + 0x25b32;
  }
  MonCtrl::ConPrintfMessage(pcVar2,iVar3,iVar1,uVar4);
LAB_00025b8c:
  MWF::ObjMsg::~ObjMsg(auStack_28);
  MWF::ObjMsg::~ObjMsg(auStack_20);
  return;
}


/* 00025bd8 */

/* MprCtrlUpmEvent::UnregisterBusPowerEvent() */

void __thiscall MprCtrlUpmEvent::UnregisterBusPowerEvent(MprCtrlUpmEvent *this)

{
  int iVar1;
  char *pcVar2;
  int iVar3;
  undefined4 uVar4;
  ParamStd_Template<unsigned_int,(MWF::Param::Type)8> aPStack_30 [8];
  undefined1 auStack_28 [8];
  undefined1 auStack_20 [8];
  undefined1 *local_18;
  undefined1 *local_14;
  
  MWF::ObjMsg::ObjMsg(auStack_20,0x6107,0x1004);
  MWF::ObjMsg::ObjMsg(auStack_28);
  MemUtil::MemSet8(&local_18,'\0',8);
  MWF::ParamStd_Template<unsigned_int,(MWF::Param::Type)8>::ParamStd_Template((uint)aPStack_30);
  MWF::ObjMsg::AddParam((uint)auStack_20,(Param *)0x1016);
  MWF::ParamStd_Template<unsigned_int,(MWF::Param::Type)8>::~ParamStd_Template(aPStack_30);
  local_14 = auStack_28;
  uVar4 = 0;
  local_18 = auStack_20;
  iVar1 = MWF::EventWrapper::SendAndRecv(*(void **)(this + 0x38),(int)&local_18,(void *)0x8,0);
  if (iVar1 == 0) {
    iVar1 = MWF::ObjMsg::GetMessageId();
    if (iVar1 == DAT_00025cdc) {
      iVar1 = MWF::ObjMsg::GetParam(auStack_28,0x1000,7,DAT_00025cdc,uVar4);
      if (iVar1 == 0) {
        MonCtrl::ConPrintfMessage(*(char **)(this + 0x2c),DAT_00025ce8 + 0x25c8a,0x444);
        goto LAB_00025ca4;
      }
      iVar1 = MWF::ParamStd_Template<int,(MWF::Param::Type)7>::GetValue();
      if (iVar1 == 0) goto LAB_00025ca4;
      uVar4 = 1099;
      pcVar2 = *(char **)(this + 0x2c);
      iVar3 = DAT_00025cec + 0x25ca2;
    }
    else {
      pcVar2 = *(char **)(this + 0x2c);
      iVar1 = MWF::ObjMsg::GetMessageId();
      uVar4 = 0x43c;
      iVar3 = DAT_00025ce4 + 0x25c6e;
    }
  }
  else {
    uVar4 = 0x436;
    pcVar2 = *(char **)(this + 0x2c);
    iVar3 = DAT_00025ce0 + 0x25c4a;
  }
  MonCtrl::ConPrintfMessage(pcVar2,iVar3,iVar1,uVar4);
LAB_00025ca4:
  MWF::ObjMsg::~ObjMsg(auStack_28);
  MWF::ObjMsg::~ObjMsg(auStack_20);
  return;
}


/* 00025cf0 */

/* MprCtrlUpmEvent::~MprCtrlUpmEvent() */

MprCtrlUpmEvent * __thiscall MprCtrlUpmEvent::~MprCtrlUpmEvent(MprCtrlUpmEvent *this)

{
  InhMgr *this_00;
  
  if (*(UpmWrapper **)(this + 8) != (UpmWrapper *)0x0) {
    UpmWrapper::ClearCallBackForHeatAlert(*(UpmWrapper **)(this + 8));
    UpmWrapper::ClearCallBackForPowerStatus(*(UpmWrapper **)(this + 8));
    UpmWrapper::ClearCallBackForBatteryLevel(*(UpmWrapper **)(this + 8));
    if (*(int **)(this + 8) != (int *)0x0) {
      (**(code **)(**(int **)(this + 8) + 4))();
    }
    *(undefined4 *)(this + 8) = 0;
  }
  if (*(void **)(this + 0x40) != (void *)0x0) {
    operator_delete(*(void **)(this + 0x40));
    *(undefined4 *)(this + 0x40) = 0;
  }
  if (*(int **)(this + 0x34) != (int *)0x0) {
    (**(code **)(**(int **)(this + 0x34) + 4))();
    *(undefined4 *)(this + 0x34) = 0;
  }
  this_00 = *(InhMgr **)(this + 0xc);
  if (this_00 != (InhMgr *)0x0) {
    MWF::InhMgr::~InhMgr(this_00);
    operator_delete(this_00);
    *(undefined4 *)(this + 0xc) = 0;
  }
  if (*(int **)(this + 0x18) != (int *)0x0) {
    (**(code **)(**(int **)(this + 0x18) + 4))();
    *(undefined4 *)(this + 0x18) = 0;
  }
  if (*(int **)(this + 0x1c) != (int *)0x0) {
    (**(code **)(**(int **)(this + 0x1c) + 4))();
    *(undefined4 *)(this + 0x1c) = 0;
  }
  if (*(int **)(this + 0x10) != (int *)0x0) {
    (**(code **)(**(int **)(this + 0x10) + 4))();
    *(undefined4 *)(this + 0x10) = 0;
  }
  if (*(int **)(this + 0x14) != (int *)0x0) {
    (**(code **)(**(int **)(this + 0x14) + 4))();
    *(undefined4 *)(this + 0x14) = 0;
  }
  if (*(int *)(this + 0x38) != 0) {
    MWF::EventWrapper::ClearCallBack();
    MWF::EventIdFactory::ReleaseId(*(uint *)(this + 0x3c));
    *(undefined4 *)(this + 0x3c) = 0;
    if (*(int **)(this + 0x38) != (int *)0x0) {
      (**(code **)(**(int **)(this + 0x38) + 4))();
    }
    *(undefined4 *)(this + 0x38) = 0;
  }
  UnregisterBusPowerEvent(this);
  *(undefined4 *)(this + 0x28) = 0;
  *(undefined4 *)(this + 0x2c) = 0;
  *(undefined4 *)(this + 0x30) = 0;
  return this;
}


/* 00025db0 */

/* MprCtrlUpmEvent::GetCurPwrSpplyState(int*, int*) */

int __thiscall MprCtrlUpmEvent::GetCurPwrSpplyState(MprCtrlUpmEvent *this,int *param_1,int *param_2)

{
  int iVar1;
  char *pcVar2;
  int iVar3;
  undefined4 uVar4;
  undefined1 auStack_30 [8];
  undefined1 auStack_28 [8];
  undefined1 *local_20;
  undefined1 *local_1c;
  
  MWF::ObjMsg::ObjMsg(auStack_28,0x6107,0x1001);
  MWF::ObjMsg::ObjMsg(auStack_30);
  if ((param_1 == (int *)0x0) || (param_2 == (int *)0x0)) {
    MonCtrl::ConPrintfMessage(*(char **)(this + 0x2c),DAT_00025f14 + 0x25dea,0,0x468);
    iVar3 = 3;
    goto LAB_00025ee2;
  }
  MemUtil::MemSet8(&local_20,'\0',8);
  local_20 = auStack_28;
  uVar4 = 0;
  local_1c = auStack_30;
  iVar3 = MWF::EventWrapper::SendAndRecv(*(void **)(this + 0x38),(int)&local_20,(void *)0x8,0);
  if (iVar3 != 0) {
    MonCtrl::ConPrintfMessage(*(char **)(this + 0x2c),DAT_00025f18 + 0x25e26,iVar3,0x475);
    goto LAB_00025ee2;
  }
  iVar1 = MWF::ObjMsg::GetMessageId();
  if (iVar1 == DAT_00025f10) {
    iVar1 = MWF::ObjMsg::GetParam(auStack_30,0x1000,7,DAT_00025f10,uVar4);
    if (iVar1 == 0) {
      uVar4 = 0x483;
      pcVar2 = *(char **)(this + 0x2c);
      iVar3 = DAT_00025f20 + 0x25e66;
    }
    else {
      iVar1 = MWF::ParamStd_Template<int,(MWF::Param::Type)7>::GetValue();
      if (iVar1 != 0) {
        uVar4 = 0x489;
        pcVar2 = *(char **)(this + 0x2c);
        iVar3 = DAT_00025f24 + 0x25e7a;
        goto LAB_00025e78;
      }
      iVar1 = MWF::ObjMsg::GetParam(auStack_30,0x1005,7);
      if (iVar1 == 0) {
        uVar4 = 0x491;
        pcVar2 = *(char **)(this + 0x2c);
        iVar3 = DAT_00025f28 + 0x25e98;
      }
      else {
        iVar1 = MWF::ParamStd_Template<int,(MWF::Param::Type)7>::GetValue();
        *param_1 = iVar1;
        if (iVar1 != 0) {
          MonCtrl::ConPrintfMessage(*(char **)(this + 0x2c),DAT_00025f2c + 0x25eac,0x497);
          iVar3 = 0xffff;
        }
        iVar1 = MWF::ObjMsg::GetParam(auStack_30,0x100e,7);
        if (iVar1 != 0) {
          iVar1 = MWF::ParamStd_Template<int,(MWF::Param::Type)7>::GetValue();
          *param_2 = iVar1;
          goto LAB_00025ee2;
        }
        uVar4 = 0x49e;
        pcVar2 = *(char **)(this + 0x2c);
        iVar3 = DAT_00025f30 + 0x25ecc;
      }
    }
    MonCtrl::ConPrintfMessage(pcVar2,iVar3,uVar4);
  }
  else {
    pcVar2 = *(char **)(this + 0x2c);
    iVar1 = MWF::ObjMsg::GetMessageId();
    uVar4 = 0x47b;
    iVar3 = DAT_00025f1c + 0x25e4c;
LAB_00025e78:
    MonCtrl::ConPrintfMessage(pcVar2,iVar3,iVar1,uVar4);
  }
  iVar3 = 0xffff;
LAB_00025ee2:
  MWF::ObjMsg::~ObjMsg(auStack_30);
  MWF::ObjMsg::~ObjMsg(auStack_28);
  return iVar3;
}


/* 00025f34 */

/* MprCtrlUpmEvent::MprCtrlUpmEvent() */

MprCtrlUpmEvent * __thiscall MprCtrlUpmEvent::MprCtrlUpmEvent(MprCtrlUpmEvent *this)

{
  char *pcVar1;
  int *piVar2;
  bool bVar3;
  bool bVar4;
  undefined4 uVar5;
  ObjLock *this_00;
  InhMgr *this_01;
  RsrcMgr *pRVar6;
  RsrcAcsr *pRVar7;
  EventWrapper *this_02;
  UpmWrapper *this_03;
  void *pvVar8;
  int iVar9;
  ushort *puVar10;
  int iVar11;
  int iVar12;
  _func_void_void_ptr_int_void_ptr_uint *p_Var13;
  uint uVar14;
  
  *this = (MprCtrlUpmEvent)0x0;
  *(undefined4 *)(this + 8) = 0;
  *(undefined4 *)(this + 0x10) = 0;
  *(undefined4 *)(this + 0x18) = 0;
  *(undefined4 *)(this + 0x14) = 0;
  *(undefined4 *)(this + 0x1c) = 0;
  *(undefined4 *)(this + 0x38) = 0;
  *(undefined4 *)(this + 0x3c) = 0;
  *(undefined4 *)(this + 4) = 0;
  rsrcInfo::Init((rsrcInfo *)(this + 0x20));
  rsrcInfo::Init((rsrcInfo *)(this + 0x24));
  iVar12 = DAT_00026260;
  uVar5 = MprCtrlMcmd::GetMonMsg();
  iVar12 = iVar12 + 0x25f6c;
  *(undefined4 *)(this + 0x28) = uVar5;
  uVar5 = MprCtrlMcmd::GetMonErr();
  *(undefined4 *)(this + 0x2c) = uVar5;
  uVar5 = MprCtrlMcmd::GetMonDbg();
  *(undefined4 *)(this + 0x30) = uVar5;
  MprCtrlLog::SetStartApiLog(0xc0,0x37);
  this_00 = operator_new(0x1c);
  MWF::ObjLock::ObjLock(this_00);
  *(ObjLock **)(this + 0x34) = this_00;
  this_01 = operator_new(0xc);
  MWF::InhMgr::InhMgr(this_01);
  *(InhMgr **)(this + 0xc) = this_01;
  pRVar6 = operator_new(0x24);
  MWF::RsrcMgr::RsrcMgr(pRVar6,0x47,0x1e);
  *(RsrcMgr **)(this + 0x10) = pRVar6;
  pRVar6 = operator_new(0x24);
  MWF::RsrcMgr::RsrcMgr(pRVar6,0x48,0x1e);
  *(RsrcMgr **)(this + 0x14) = pRVar6;
  pRVar7 = operator_new(0x28);
  uVar5 = *(undefined4 *)(iVar12 + DAT_00026264);
  MWF::RsrcAcsr::RsrcAcsr(pRVar7,0x5d,this,*(undefined4 *)(iVar12 + DAT_00026268),uVar5);
  *(RsrcAcsr **)(this + 0x18) = pRVar7;
  pRVar7 = operator_new(0x28);
  MWF::RsrcAcsr::RsrcAcsr(pRVar7,0x5f,this,*(undefined4 *)(iVar12 + DAT_0002626c),uVar5);
  *(RsrcAcsr **)(this + 0x1c) = pRVar7;
  this_02 = operator_new(0x18);
  MWF::EventWrapper::EventWrapper(this_02);
  *(EventWrapper **)(this + 0x38) = this_02;
  MWF::EventIdFactory::GetId(199,(uint *)(this + 0x3c));
  MWF::EventWrapper::SetSendId(*(uint *)(this + 0x38));
  this_03 = operator_new(0x34);
  UpmWrapper::UpmWrapper(this_03);
  *(UpmWrapper **)(this + 8) = this_03;
  pvVar8 = operator_new(0x74);
  *(void **)(this + 0x40) = pvVar8;
  MemUtil::MemSet8(pvVar8,'\0',0x74);
  iVar9 = *(int *)(this + 0x40);
  iVar9 = UpmWrapper::GetAcBatteryCheckInfo(iVar9,iVar9 + 4,iVar9 + 8,0);
  if (iVar9 == 0) {
    MonCtrl::ConPrintfMessage(*(char **)(this + 0x30),DAT_00026274 + 0x2605e,0);
    MonCtrl::ConPrintfMessage(*(char **)(this + 0x30),DAT_00026278 + 0x26068);
    MonCtrl::ConPrintfMessage
              (*(char **)(this + 0x30),DAT_0002627c + 0x26076,**(undefined4 **)(this + 0x40));
    MonCtrl::ConPrintfMessage
              (*(char **)(this + 0x30),DAT_00026280 + 0x26084,
               *(undefined4 *)(*(int *)(this + 0x40) + 4));
    if (*(int *)(*(int *)(this + 0x40) + 4) != 0) {
      MonCtrl::ConPrintfMessage(*(char **)(this + 0x30),DAT_00026284 + 0x26094);
    }
    for (uVar14 = 0; puVar10 = *(ushort **)(this + 0x40), uVar14 < *(uint *)(puVar10 + 2);
        uVar14 = uVar14 + 1) {
      iVar9 = uVar14 * 0x1c;
      MonCtrl::ConPrintfMessage
                (*(char **)(this + 0x30),DAT_00026288 + 0x260aa,
                 *(undefined4 *)(puVar10 + uVar14 * 0xe + 8));
      MonCtrl::ConPrintfMessage
                (*(char **)(this + 0x30),DAT_0002628c + 0x260c0,
                 *(undefined4 *)(*(int *)(this + 0x40) + iVar9 + 8));
      MonCtrl::ConPrintfMessage
                (*(char **)(this + 0x30),DAT_00026290 + 0x260d0,
                 *(undefined4 *)(*(int *)(this + 0x40) + iVar9 + 0xc));
      MonCtrl::ConPrintfMessage
                (*(char **)(this + 0x30),DAT_00026294 + 0x260e0,
                 (uint)*(ushort *)(*(int *)(this + 0x40) + iVar9 + 0x18));
      MonCtrl::ConPrintfMessage
                (*(char **)(this + 0x30),DAT_00026298 + 0x260f0,
                 *(undefined4 *)(*(int *)(this + 0x40) + iVar9 + 0x14));
      MonCtrl::ConPrintfMessage
                (*(char **)(this + 0x30),DAT_0002629c + 0x26100,
                 *(undefined4 *)(*(int *)(this + 0x40) + iVar9 + 0x1c));
    }
    MprCtrlLog::SetParamLog(0xc2,0,0,*puVar10,0x7c);
    uVar5 = GetCurPwrSpplyState(this,(int *)(*(int *)(this + 0x40) + 0x6c),
                                (int *)(*(int *)(this + 0x40) + 0x70));
    MonCtrl::ConPrintfMessage(*(char **)(this + 0x30),DAT_000262a0 + 0x26130,uVar5);
    MonCtrl::ConPrintfMessage(*(char **)(this + 0x30),DAT_000262a4 + 0x26140);
    MonCtrl::ConPrintfMessage(*(char **)(this + 0x30),DAT_000262a8 + 0x2614a);
    MonCtrl::ConPrintfMessage
              (*(char **)(this + 0x30),DAT_000262ac + 0x26158,
               *(undefined4 *)(*(int *)(this + 0x40) + 0x6c));
    MonCtrl::ConPrintfMessage
              (*(char **)(this + 0x30),DAT_000262b0 + 0x26166,
               *(undefined4 *)(*(int *)(this + 0x40) + 0x70));
    MprCtrlLog::SetParamLog
              (0xc6,(ushort)uVar5,*(ushort *)(*(int *)(this + 0x40) + 0x6c),
               *(ushort *)(*(int *)(this + 0x40) + 0x70),0x90);
    if ((**(int **)(this + 0x40) == 1) && ((*(int **)(this + 0x40))[0x1c] != 2)) {
      UpdateResourse(this,2,true);
      *this = (MprCtrlUpmEvent)0x1;
      UpdateInhInfo(this,0,1);
      iVar11 = *(int *)(this + 0x40);
      iVar9 = 0;
      piVar2 = (int *)(iVar11 + 4);
      bVar3 = true;
      bVar4 = true;
      while (iVar9 != *piVar2) {
        if ((*(uint *)(iVar11 + 0xc) < 2) && (*(short *)(iVar11 + 0x18) != 0)) {
          bVar3 = false;
        }
        pcVar1 = (char *)(iVar11 + 0x20);
        iVar9 = iVar9 + 1;
        iVar11 = iVar11 + 0x1c;
        if (*pcVar1 != '\0') {
          bVar4 = false;
        }
      }
      if (bVar3) {
        UpdateInhInfo(this,1,1);
      }
      if (bVar4) {
        UpdateInhInfo(this,3,1);
      }
    }
  }
  else {
    MonCtrl::ConPrintfMessage(*(char **)(this + 0x2c),DAT_00026270 + 0x26052,iVar9);
  }
  iVar9 = *(int *)(this + 0x40);
  *(undefined4 *)(iVar9 + 100) = 1;
  *(undefined4 *)(iVar9 + 0x5c) = 0;
  *(undefined4 *)(iVar9 + 0x60) = 0xffffffff;
  *(undefined4 *)(iVar9 + 0x68) = 0xffffffff;
  iVar9 = UpmWrapper::GetTemperatureRange(0,iVar9 + 0x60);
  if (iVar9 == 0) {
    if ((*(int *)(*(int *)(this + 0x40) + 0x60) == 2) ||
       (*(int *)(*(int *)(this + 0x40) + 0x60) == 4)) {
      MonCtrl::ConPrintfMessage(*(char **)(this + 0x2c),DAT_000262b8 + 0x2622a,0);
      UpdateResourse(this,1,true);
      UpdateInhInfo(this,2,1);
    }
  }
  else {
    MonCtrl::ConPrintfMessage(*(char **)(this + 0x2c),DAT_000262b4 + 0x26212,iVar9);
  }
  iVar9 = UpmWrapper::GetTemperatureRange
                    (*(undefined4 *)(*(int *)(this + 0x40) + 100),*(int *)(this + 0x40) + 0x68);
  if (iVar9 == 0) {
    if ((*(int *)(*(int *)(this + 0x40) + 0x68) == 2) ||
       (*(int *)(*(int *)(this + 0x40) + 0x68) == 4)) {
      MonCtrl::ConPrintfMessage(*(char **)(this + 0x2c),DAT_00026354 + 0x262d4,0);
      UpdateResourse(this,1,true);
      UpdateInhInfo(this,2,1);
    }
  }
  else {
    MonCtrl::ConPrintfMessage(*(char **)(this + 0x2c),DAT_000262bc + 0x26256,iVar9);
  }
  p_Var13 = *(_func_void_void_ptr_int_void_ptr_uint **)(iVar12 + DAT_00026358);
  UpmWrapper::RegisterCallBackForHeatAlert(*(UpmWrapper **)(this + 8),199,p_Var13,this);
  UpmWrapper::RegisterCallBackForPowerStatus(*(UpmWrapper **)(this + 8),199,p_Var13,this);
  UpmWrapper::RegisterCallBackForBatteryLevel(*(UpmWrapper **)(this + 8),199,p_Var13,this);
  MWF::EventWrapper::RegisterCallBack
            (*(uint *)(this + 0x38),*(_func_void_void_ptr_int_void_ptr_uint **)(this + 0x3c),
             *(void **)(iVar12 + DAT_0002635c));
  RegisterBusPowerEvent(this);
  MprCtrlLog::SetEndApiLog(0xc0,0,0x10a);
  return this;
}


/* 00026360 */

/* MprCtrlStillMgr::~MprCtrlStillMgr() */

MprCtrlStillMgr * __thiscall MprCtrlStillMgr::~MprCtrlStillMgr(MprCtrlStillMgr *this)

{
  void *pvVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  
  *(int *)this = *(int *)(DAT_00026724 + 0x26370 + DAT_00026728) + 8;
  if (*(void **)(this + 4) != (void *)0x0) {
    operator_delete(*(void **)(this + 4));
    *(undefined4 *)(this + 4) = 0;
  }
  if (*(int *)(this + 8) != 0) {
    iVar2 = 0;
    iVar5 = *(int *)(*(int *)(this + 8) + 8);
    for (uVar3 = 0; uVar3 < *(uint *)(*(int *)(this + 8) + 0xc); uVar3 = uVar3 + 1) {
      iVar4 = iVar5 + iVar2;
      pvVar1 = *(void **)(iVar4 + 4);
      if (pvVar1 != (void *)0x0) {
        operator_delete__(pvVar1);
      }
      iVar2 = iVar2 + 8;
      *(undefined4 *)(iVar4 + 4) = 0;
    }
    iVar2 = 0;
    iVar5 = *(int *)(*(int *)(this + 8) + 0xe4);
    for (uVar3 = 0; uVar3 < *(uint *)(*(int *)(this + 8) + 0xe8); uVar3 = uVar3 + 1) {
      iVar4 = iVar5 + iVar2;
      pvVar1 = *(void **)(iVar4 + 4);
      if (pvVar1 != (void *)0x0) {
        operator_delete__(pvVar1);
      }
      iVar2 = iVar2 + 8;
      *(undefined4 *)(iVar4 + 4) = 0;
    }
    iVar2 = 0;
    iVar5 = *(int *)(*(int *)(this + 8) + 0x1c);
    for (uVar3 = 0; uVar3 < *(uint *)(*(int *)(this + 8) + 0x20); uVar3 = uVar3 + 1) {
      iVar4 = iVar5 + iVar2;
      pvVar1 = *(void **)(iVar4 + 4);
      if (pvVar1 != (void *)0x0) {
        operator_delete__(pvVar1);
      }
      iVar2 = iVar2 + 8;
      *(undefined4 *)(iVar4 + 4) = 0;
    }
    iVar2 = 0;
    iVar5 = *(int *)(*(int *)(this + 8) + 0xf8);
    for (uVar3 = 0; uVar3 < *(uint *)(*(int *)(this + 8) + 0xfc); uVar3 = uVar3 + 1) {
      iVar4 = iVar5 + iVar2;
      pvVar1 = *(void **)(iVar4 + 4);
      if (pvVar1 != (void *)0x0) {
        operator_delete__(pvVar1);
      }
      iVar2 = iVar2 + 8;
      *(undefined4 *)(iVar4 + 4) = 0;
    }
    iVar2 = 0;
    iVar5 = *(int *)(*(int *)(this + 8) + 0x30);
    for (uVar3 = 0; uVar3 < *(uint *)(*(int *)(this + 8) + 0x34); uVar3 = uVar3 + 1) {
      iVar4 = iVar5 + iVar2;
      pvVar1 = *(void **)(iVar4 + 4);
      if (pvVar1 != (void *)0x0) {
        operator_delete__(pvVar1);
      }
      iVar2 = iVar2 + 8;
      *(undefined4 *)(iVar4 + 4) = 0;
    }
    iVar2 = 0;
    iVar5 = *(int *)(*(int *)(this + 8) + 0x10c);
    for (uVar3 = 0; uVar3 < *(uint *)(*(int *)(this + 8) + 0x110); uVar3 = uVar3 + 1) {
      iVar4 = iVar5 + iVar2;
      pvVar1 = *(void **)(iVar4 + 4);
      if (pvVar1 != (void *)0x0) {
        operator_delete__(pvVar1);
      }
      iVar2 = iVar2 + 8;
      *(undefined4 *)(iVar4 + 4) = 0;
    }
    iVar2 = 0;
    iVar5 = *(int *)(*(int *)(this + 8) + 0x44);
    for (uVar3 = 0; uVar3 < *(uint *)(*(int *)(this + 8) + 0x48); uVar3 = uVar3 + 1) {
      iVar4 = iVar5 + iVar2;
      pvVar1 = *(void **)(iVar4 + 4);
      if (pvVar1 != (void *)0x0) {
        operator_delete__(pvVar1);
      }
      iVar2 = iVar2 + 8;
      *(undefined4 *)(iVar4 + 4) = 0;
    }
    iVar2 = 0;
    iVar5 = *(int *)(*(int *)(this + 8) + 0x120);
    for (uVar3 = 0; uVar3 < *(uint *)(*(int *)(this + 8) + 0x124); uVar3 = uVar3 + 1) {
      iVar4 = iVar5 + iVar2;
      pvVar1 = *(void **)(iVar4 + 4);
      if (pvVar1 != (void *)0x0) {
        operator_delete__(pvVar1);
      }
      iVar2 = iVar2 + 8;
      *(undefined4 *)(iVar4 + 4) = 0;
    }
    iVar2 = 0;
    iVar5 = *(int *)(*(int *)(this + 8) + 0x58);
    for (uVar3 = 0; uVar3 < *(uint *)(*(int *)(this + 8) + 0x5c); uVar3 = uVar3 + 1) {
      iVar4 = iVar5 + iVar2;
      pvVar1 = *(void **)(iVar4 + 4);
      if (pvVar1 != (void *)0x0) {
        operator_delete__(pvVar1);
      }
      iVar2 = iVar2 + 8;
      *(undefined4 *)(iVar4 + 4) = 0;
    }
    iVar2 = 0;
    iVar5 = *(int *)(*(int *)(this + 8) + 0x134);
    for (uVar3 = 0; uVar3 < *(uint *)(*(int *)(this + 8) + 0x138); uVar3 = uVar3 + 1) {
      iVar4 = iVar5 + iVar2;
      pvVar1 = *(void **)(iVar4 + 4);
      if (pvVar1 != (void *)0x0) {
        operator_delete__(pvVar1);
      }
      iVar2 = iVar2 + 8;
      *(undefined4 *)(iVar4 + 4) = 0;
    }
    iVar2 = 0;
    iVar5 = *(int *)(*(int *)(this + 8) + 0x6c);
    for (uVar3 = 0; uVar3 < *(uint *)(*(int *)(this + 8) + 0x70); uVar3 = uVar3 + 1) {
      iVar4 = iVar5 + iVar2;
      pvVar1 = *(void **)(iVar4 + 4);
      if (pvVar1 != (void *)0x0) {
        operator_delete__(pvVar1);
      }
      iVar2 = iVar2 + 8;
      *(undefined4 *)(iVar4 + 4) = 0;
    }
    iVar2 = 0;
    iVar5 = *(int *)(*(int *)(this + 8) + 0x148);
    for (uVar3 = 0; uVar3 < *(uint *)(*(int *)(this + 8) + 0x14c); uVar3 = uVar3 + 1) {
      iVar4 = iVar5 + iVar2;
      pvVar1 = *(void **)(iVar4 + 4);
      if (pvVar1 != (void *)0x0) {
        operator_delete__(pvVar1);
      }
      iVar2 = iVar2 + 8;
      *(undefined4 *)(iVar4 + 4) = 0;
    }
    iVar2 = 0;
    iVar5 = *(int *)(*(int *)(this + 8) + 0x80);
    for (uVar3 = 0; uVar3 < *(uint *)(*(int *)(this + 8) + 0x84); uVar3 = uVar3 + 1) {
      iVar4 = iVar5 + iVar2;
      pvVar1 = *(void **)(iVar4 + 4);
      if (pvVar1 != (void *)0x0) {
        operator_delete__(pvVar1);
      }
      iVar2 = iVar2 + 8;
      *(undefined4 *)(iVar4 + 4) = 0;
    }
    iVar2 = 0;
    iVar5 = *(int *)(*(int *)(this + 8) + 0x15c);
    for (uVar3 = 0; uVar3 < *(uint *)(*(int *)(this + 8) + 0x160); uVar3 = uVar3 + 1) {
      iVar4 = iVar5 + iVar2;
      pvVar1 = *(void **)(iVar4 + 4);
      if (pvVar1 != (void *)0x0) {
        operator_delete__(pvVar1);
      }
      iVar2 = iVar2 + 8;
      *(undefined4 *)(iVar4 + 4) = 0;
    }
    iVar2 = 0;
    iVar5 = *(int *)(*(int *)(this + 8) + 0x94);
    for (uVar3 = 0; uVar3 < *(uint *)(*(int *)(this + 8) + 0x98); uVar3 = uVar3 + 1) {
      iVar4 = iVar5 + iVar2;
      pvVar1 = *(void **)(iVar4 + 4);
      if (pvVar1 != (void *)0x0) {
        operator_delete__(pvVar1);
      }
      iVar2 = iVar2 + 8;
      *(undefined4 *)(iVar4 + 4) = 0;
    }
    iVar2 = 0;
    iVar5 = *(int *)(*(int *)(this + 8) + 0xa8);
    for (uVar3 = 0; uVar3 < *(uint *)(*(int *)(this + 8) + 0xac); uVar3 = uVar3 + 1) {
      iVar4 = iVar5 + iVar2;
      pvVar1 = *(void **)(iVar4 + 4);
      if (pvVar1 != (void *)0x0) {
        operator_delete__(pvVar1);
      }
      iVar2 = iVar2 + 8;
      *(undefined4 *)(iVar4 + 4) = 0;
    }
    iVar2 = 0;
    iVar5 = *(int *)(*(int *)(this + 8) + 0x170);
    for (uVar3 = 0; uVar3 < *(uint *)(*(int *)(this + 8) + 0x174); uVar3 = uVar3 + 1) {
      iVar4 = iVar5 + iVar2;
      pvVar1 = *(void **)(iVar4 + 4);
      if (pvVar1 != (void *)0x0) {
        operator_delete__(pvVar1);
      }
      iVar2 = iVar2 + 8;
      *(undefined4 *)(iVar4 + 4) = 0;
    }
    iVar2 = 0;
    iVar5 = *(int *)(*(int *)(this + 8) + 0xbc);
    for (uVar3 = 0; uVar3 < *(uint *)(*(int *)(this + 8) + 0xc0); uVar3 = uVar3 + 1) {
      iVar4 = iVar5 + iVar2;
      pvVar1 = *(void **)(iVar4 + 4);
      if (pvVar1 != (void *)0x0) {
        operator_delete__(pvVar1);
      }
      iVar2 = iVar2 + 8;
      *(undefined4 *)(iVar4 + 4) = 0;
    }
    iVar2 = 0;
    iVar5 = *(int *)(*(int *)(this + 8) + 0x184);
    for (uVar3 = 0; uVar3 < *(uint *)(*(int *)(this + 8) + 0x188); uVar3 = uVar3 + 1) {
      iVar4 = iVar5 + iVar2;
      pvVar1 = *(void **)(iVar4 + 4);
      if (pvVar1 != (void *)0x0) {
        operator_delete__(pvVar1);
      }
      iVar2 = iVar2 + 8;
      *(undefined4 *)(iVar4 + 4) = 0;
    }
    iVar2 = 0;
    iVar5 = *(int *)(*(int *)(this + 8) + 0xd0);
    for (uVar3 = 0; uVar3 < *(uint *)(*(int *)(this + 8) + 0xd4); uVar3 = uVar3 + 1) {
      iVar4 = iVar5 + iVar2;
      pvVar1 = *(void **)(iVar4 + 4);
      if (pvVar1 != (void *)0x0) {
        operator_delete__(pvVar1);
      }
      iVar2 = iVar2 + 8;
      *(undefined4 *)(iVar4 + 4) = 0;
    }
    iVar2 = 0;
    iVar5 = *(int *)(*(int *)(this + 8) + 0x198);
    for (uVar3 = 0; uVar3 < *(uint *)(*(int *)(this + 8) + 0x19c); uVar3 = uVar3 + 1) {
      iVar4 = iVar5 + iVar2;
      pvVar1 = *(void **)(iVar4 + 4);
      if (pvVar1 != (void *)0x0) {
        operator_delete__(pvVar1);
      }
      iVar2 = iVar2 + 8;
      *(undefined4 *)(iVar4 + 4) = 0;
    }
  }
  *(undefined4 *)(this + 8) = 0;
  return this;
}


/* 0002672c */

/* MprCtrlStillMgr::~MprCtrlStillMgr() */

MprCtrlStillMgr * __thiscall MprCtrlStillMgr::~MprCtrlStillMgr(MprCtrlStillMgr *this)

{
  ~MprCtrlStillMgr(this);
  operator_delete(this);
  return this;
}


/* 00026740 */

/* MprCtrlStillMgr::GetStillSizeRow(unsigned int) */

int __thiscall MprCtrlStillMgr::GetStillSizeRow(MprCtrlStillMgr *this,uint param_1)

{
  return *(int *)(this + 4) + param_1 * 8;
}


/* 0002674c */

/* MprCtrlStillMgr::Exchg_Byte(int) */

int __thiscall MprCtrlStillMgr::Exchg_Byte(MprCtrlStillMgr *this,int param_1)

{
  return param_1 << 10;
}


/* 00026754 */

/* MprCtrlStillMgr::Calc_Align(int) */

uint __thiscall MprCtrlStillMgr::Calc_Align(MprCtrlStillMgr *this,int param_1)

{
  return param_1 + 0xfffU & 0xfffff000;
}


/* 00026768 */

/* MprCtrlStillMgr::IsRecordingSCN(unsigned int) */

bool __thiscall MprCtrlStillMgr::IsRecordingSCN(MprCtrlStillMgr *this,uint param_1)

{
  return DAT_00026778 < param_1;
}


/* 0002677c */

/* MprCtrlStillMgr::MprCtrlStillMgr() */

MprCtrlStillMgr * __thiscall MprCtrlStillMgr::MprCtrlStillMgr(MprCtrlStillMgr *this)

{
  undefined4 uVar1;
  _StillSizeTable *this_00;
  
  *(int *)this = *(int *)(DAT_000267c4 + 0x26784 + DAT_000267c8) + 8;
  uVar1 = MprCtrlMcmd::GetMonMsg();
  *(undefined4 *)(this + 0x10) = uVar1;
  uVar1 = MprCtrlMcmd::GetMonErr();
  *(undefined4 *)(this + 0x14) = uVar1;
  uVar1 = MprCtrlMcmd::GetMonDbg();
  *(undefined4 *)(this + 0x18) = uVar1;
  this_00 = operator_new(0x318);
  MprCtrlStill::_StillSizeTable::_StillSizeTable(this_00);
  *(_StillSizeTable **)(this + 4) = this_00;
  *(undefined4 *)(this + 8) = 0;
  *(undefined4 *)(this + 0xc) = 0;
  MemUtil::MemSet8(this_00,'\0',0x318);
  return this;
}


/* 000267cc */

/* MprCtrlStillMgr::GetBackupStillSize() */

int __thiscall MprCtrlStillMgr::GetBackupStillSize(MprCtrlStillMgr *this)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  
  iVar2 = 0;
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x18),DAT_00026a50 + 0x267d6);
  do {
    uVar3 = *(uint *)(DAT_00026a54 + 0x267ea + iVar2 * 8);
    iVar1 = BackupLib::GetEepData(uVar3,'\b',(void *)(*(int *)(this + 4) + iVar2 * 8));
    if (iVar1 < 0) {
      MonCtrl::ConPrintfMessage(*(char **)(this + 0x14),DAT_00026a58 + 0x26804,uVar3);
      break;
    }
    iVar2 = iVar2 + 1;
  } while (iVar2 != 0x14);
  iVar2 = 0x14;
  do {
    uVar3 = *(uint *)(MprCtrlStillMgr + DAT_00026a5c + iVar2 * 8);
    iVar1 = BackupLib::GetEepData(uVar3,'\b',(void *)(*(int *)(this + 4) + iVar2 * 8));
    if (iVar1 < 0) {
      MonCtrl::ConPrintfMessage(*(char **)(this + 0x14),DAT_00026a60 + 0x26838,uVar3);
      break;
    }
    iVar2 = iVar2 + 1;
  } while (iVar2 != 0x28);
  iVar2 = 0x28;
  do {
    uVar3 = *(uint *)(DAT_00026a64 + iVar2 * 8 + 0x26710);
    iVar1 = BackupLib::GetEepData(uVar3,'\b',(void *)(*(int *)(this + 4) + iVar2 * 8));
    if (iVar1 < 0) {
      MonCtrl::ConPrintfMessage(*(char **)(this + 0x14),DAT_00026a68 + 0x2686e,uVar3);
      break;
    }
    iVar2 = iVar2 + 1;
  } while (iVar2 != 0x30);
  iVar2 = 0x30;
  do {
    uVar3 = *(uint *)(DAT_00026a6c + iVar2 * 8 + 0x26706);
    iVar1 = BackupLib::GetEepData(uVar3,'\b',(void *)(*(int *)(this + 4) + iVar2 * 8));
    if (iVar1 < 0) {
      MonCtrl::ConPrintfMessage(*(char **)(this + 0x14),DAT_00026a70 + 0x268a4,uVar3);
      break;
    }
    iVar2 = iVar2 + 1;
  } while (iVar2 != 0x38);
  iVar2 = 0x38;
  do {
    uVar3 = *(uint *)(DAT_00026a74 + iVar2 * 8 + 0x266fc);
    iVar1 = BackupLib::GetEepData(uVar3,'\b',(void *)(*(int *)(this + 4) + iVar2 * 8));
    if (iVar1 < 0) {
      MonCtrl::ConPrintfMessage(*(char **)(this + 0x14),DAT_00026a78 + 0x268da,uVar3);
      break;
    }
    iVar2 = iVar2 + 1;
  } while (iVar2 != 0x3b);
  iVar2 = 0x3b;
  do {
    uVar3 = *(uint *)(DAT_00026a7c + iVar2 * 8 + 0x2671a);
    iVar1 = BackupLib::GetEepData(uVar3,'\b',(void *)(*(int *)(this + 4) + iVar2 * 8));
    if (iVar1 < 0) {
      MonCtrl::ConPrintfMessage(*(char **)(this + 0x14),DAT_00026a80 + 0x26910,uVar3);
      break;
    }
    iVar2 = iVar2 + 1;
  } while (iVar2 != 0x3e);
  iVar2 = BackupLib::GetEepData(DAT_00026a40,'\b',(void *)(*(int *)(this + 4) + 0x1f0));
  if (iVar2 < 0) {
    MonCtrl::ConPrintfMessage(*(char **)(this + 0x14),DAT_00026a84 + 0x26936,DAT_00026a40);
  }
  iVar2 = BackupLib::GetEepData(DAT_00026a44,'\b',(void *)(*(int *)(this + 4) + 0x1f8));
  if (iVar2 < 0) {
    MonCtrl::ConPrintfMessage(*(char **)(this + 0x14),DAT_00026a88 + 0x26954,DAT_00026a44);
  }
  iVar2 = 0x40;
  do {
    uVar3 = *(uint *)(DAT_00026a8c + iVar2 * 8 + 0x26764);
    iVar1 = BackupLib::GetEepData(uVar3,'\b',(void *)(*(int *)(this + 4) + iVar2 * 8));
    if (iVar1 < 0) {
      MonCtrl::ConPrintfMessage(*(char **)(this + 0x14),DAT_00026a90 + 0x26982,uVar3);
      break;
    }
    iVar2 = iVar2 + 1;
  } while (iVar2 != 0x4f);
  iVar2 = 0x4f;
  do {
    uVar3 = *(uint *)(&UNK_00026722 + DAT_00026a94 + iVar2 * 8);
    iVar1 = BackupLib::GetEepData(uVar3,'\b',(void *)(*(int *)(this + 4) + iVar2 * 8));
    if (iVar1 < 0) {
      MonCtrl::ConPrintfMessage(*(char **)(this + 0x14),DAT_00026a98 + 0x269b8,uVar3);
      break;
    }
    iVar2 = iVar2 + 1;
  } while (iVar2 != 0x5e);
  iVar2 = BackupLib::GetEepData(DAT_00026a48,'\b',(void *)(*(int *)(this + 4) + 0x2f0));
  if (iVar2 < 0) {
    MonCtrl::ConPrintfMessage(*(char **)(this + 0x14),DAT_00026a9c + 0x269de,DAT_00026a48);
  }
  iVar2 = BackupLib::GetEepData(DAT_00026a4c,'\b',(void *)(*(int *)(this + 4) + 0x2f8));
  if (iVar2 < 0) {
    MonCtrl::ConPrintfMessage(*(char **)(this + 0x14),DAT_00026aa0 + 0x269fc,DAT_00026a4c);
  }
  iVar2 = 0x60;
  do {
    uVar3 = *(uint *)(DAT_00026aa4 + iVar2 * 8 + 0x2670c);
    iVar1 = BackupLib::GetEepData(uVar3,'\b',(void *)(*(int *)(this + 4) + iVar2 * 8));
    if (iVar1 < 0) {
      MonCtrl::ConPrintfMessage(*(char **)(this + 0x14),DAT_00026aa8 + 0x26a2e,uVar3,iVar1);
      return iVar1;
    }
    iVar2 = iVar2 + 1;
  } while (iVar2 != 99);
  return iVar1;
}


/* 00026aac */

/* MprCtrlStillMgr::GetStillSize(unsigned short, unsigned short, DefStruct::StillSize*) */

undefined4 __thiscall
MprCtrlStillMgr::GetStillSize
          (MprCtrlStillMgr *this,ushort param_1,ushort param_2,StillSize *param_3)

{
  int extraout_r1;
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  
  iVar2 = 0;
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x18),DAT_00026b44 + 0x26ac0);
  iVar5 = *(int *)(this + 4);
  iVar4 = 0;
  iVar1 = 0;
  do {
    if (((uint)*(ushort *)(iVar5 + iVar2) == (uint)param_1) &&
       ((uint)*(ushort *)(iVar5 + iVar2 + 2) == (uint)param_2)) {
      uVar3 = 1;
      *(int *)param_3 = iVar1;
      goto LAB_00026b12;
    }
    __aeabi_idivmod(iVar4,5);
    iVar4 = iVar4 + 1;
    iVar2 = iVar2 + 8;
    if (extraout_r1 == 4) {
      iVar1 = iVar1 + 1;
    }
  } while (iVar4 != 0x28);
  uVar3 = 0;
LAB_00026b12:
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x18),DAT_00026b48 + 0x26b1c,(uint)param_1);
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x18),DAT_00026b4c + 0x26b28,(uint)param_2);
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x18),DAT_00026b50 + 0x26b34,iVar1);
  return uVar3;
}


/* 00026b54 */

/* MprCtrlStillMgr::GetStillRecInfo(DefStruct::StillSizeInfo*, int*, int*, unsigned int*) */

undefined4 __thiscall
MprCtrlStillMgr::GetStillRecInfo
          (MprCtrlStillMgr *this,StillSizeInfo *param_1,int *param_2,int *param_3,uint *param_4)

{
  char *pcVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  int iVar7;
  undefined4 uVar8;
  
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x18),DAT_00026d0c + 0x26b68);
  switch(*(undefined4 *)param_1) {
  case 0:
    switch(*(undefined4 *)(param_1 + 8)) {
    case 0:
      iVar5 = *(int *)(param_1 + 0x14);
      iVar2 = *(int *)(param_1 + 0x18);
      iVar3 = DAT_00026d10 + 0x26b9a;
      iVar4 = *(int *)(param_1 + 0xc);
      iVar7 = *(int *)(param_1 + 4);
      break;
    case 1:
      iVar5 = *(int *)(param_1 + 0x14);
      iVar2 = *(int *)(param_1 + 0x18);
      iVar3 = DAT_00026d14 + 0x26ba8;
      iVar4 = *(int *)(param_1 + 0xc);
      iVar7 = *(int *)(param_1 + 4);
      break;
    case 2:
      uVar6 = 10;
      iVar7 = *(int *)(param_1 + 0x18) * 6 + *(int *)(param_1 + 0xc) * 3 + *(int *)(param_1 + 4);
      iVar4 = *(int *)(DAT_00026d18 + 0x26be0 + iVar7 * 8);
      iVar7 = *(int *)(DAT_00026d18 + 0x26be0 + iVar7 * 8 + 4);
      goto LAB_00026c3e;
    default:
      pcVar1 = *(char **)(this + 0x14);
      iVar7 = DAT_00026d20 + 0x26c04;
LAB_00026c6c:
      MonCtrl::ConPrintfMessage(pcVar1,iVar7);
      goto switchD_00026b76_default;
    case 5:
      iVar5 = *(int *)(param_1 + 0x14);
      iVar4 = *(int *)(param_1 + 0x18);
      iVar2 = DAT_00026d1c + 0x26bf8;
      iVar3 = *(int *)(param_1 + 0xc);
      iVar7 = *(int *)(param_1 + 4);
      goto LAB_00026c88;
    }
    uVar6 = 10;
    iVar7 = iVar2 * 6 + iVar5 * 0x1e + iVar4 * 3 + iVar7;
    iVar4 = *(int *)(iVar3 + iVar7 * 8);
    iVar7 = *(int *)(iVar3 + iVar7 * 8 + 4);
    goto LAB_00026c3e;
  case 1:
    iVar7 = *(int *)(param_1 + 8);
    if (iVar7 == 3) {
      iVar5 = *(int *)(param_1 + 0x14);
      iVar4 = *(int *)(param_1 + 0x18);
      iVar2 = DAT_00026d28 + 0x26c4e;
      iVar3 = *(int *)(param_1 + 0xc);
      iVar7 = *(int *)(param_1 + 4);
    }
    else {
      if (iVar7 != 4) {
        if (iVar7 != 0) {
          pcVar1 = *(char **)(this + 0x14);
          iVar7 = DAT_00026d30 + 0x26c6e;
          goto LAB_00026c6c;
        }
        iVar7 = *(int *)(param_1 + 0x18) * 6 + *(int *)(param_1 + 0x14) * 0x18 +
                *(int *)(param_1 + 0xc) * 3 + *(int *)(param_1 + 4);
        iVar4 = *(int *)(DAT_00026d24 + 0x26c2e + iVar7 * 8);
        iVar7 = *(int *)(DAT_00026d24 + 0x26c2e + iVar7 * 8 + 4);
        uVar6 = 0;
        goto LAB_00026c3e;
      }
      iVar5 = *(int *)(param_1 + 0x14);
      iVar4 = *(int *)(param_1 + 0x18);
      iVar2 = DAT_00026d2c + 0x26c5c;
      iVar3 = *(int *)(param_1 + 0xc);
      iVar7 = *(int *)(param_1 + 4);
    }
    iVar5 = iVar5 * 0x12;
    goto LAB_00026c8e;
  case 2:
    iVar4 = *(int *)(param_1 + 0xc);
    iVar7 = *(int *)(param_1 + 4);
    iVar2 = DAT_00026d34 + 0x26c7c;
    break;
  case 3:
    iVar5 = *(int *)(param_1 + 0x14);
    iVar4 = *(int *)(param_1 + 0x18);
    iVar2 = DAT_00026d38 + 0x26c86;
    iVar3 = *(int *)(param_1 + 0xc);
    iVar7 = *(int *)(param_1 + 4);
LAB_00026c88:
    iVar5 = iVar5 * 0x1e;
LAB_00026c8e:
    iVar7 = iVar4 * 6 + iVar5 + iVar3 * 3 + iVar7;
    goto LAB_00026cb4;
  case 4:
    iVar4 = *(int *)(param_1 + 0xc);
    iVar7 = *(int *)(param_1 + 4);
    iVar2 = DAT_00026d3c + 0x26ca6;
    break;
  case 5:
    iVar4 = *(int *)(param_1 + 0x14);
    iVar7 = *(int *)(param_1 + 4);
    iVar2 = DAT_00026d40 + 0x26cb0;
    break;
  default:
switchD_00026b76_default:
    uVar6 = 0;
    iVar7 = 0;
    iVar4 = 0;
    uVar8 = 0;
    goto LAB_00026cca;
  }
  iVar7 = iVar4 * 3 + iVar7;
LAB_00026cb4:
  iVar4 = *(int *)(iVar2 + iVar7 * 8);
  uVar6 = 0;
  iVar7 = *(int *)(iVar2 + iVar7 * 8 + 4);
LAB_00026c3e:
  uVar8 = 1;
LAB_00026cca:
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x18),DAT_00026d44 + 0x26cd4,iVar4);
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x18),DAT_00026d48 + 0x26ce2,iVar7);
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x18),DAT_00026d4c + 0x26cee,uVar6);
  *param_2 = iVar4;
  *param_3 = iVar7;
  *param_4 = uVar6;
  return uVar8;
}


/* 00026d50 */

/* MprCtrlStillMgr::GetDualRecStillMode() */

uint MprCtrlStillMgr::GetDualRecStillMode(void)

{
  int in_r0;
  uint uVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  uint uVar7;
  int iVar8;
  
  MonCtrl::ConPrintfMessage(*(char **)(in_r0 + 0x18),DAT_00026dbc + 0x26d60);
  iVar5 = *(int *)(in_r0 + 8);
  uVar6 = 0;
  if (iVar5 != 0) {
    iVar4 = 0;
    uVar1 = 0;
    uVar6 = 0;
    for (uVar3 = 0; uVar3 < *(uint *)(iVar5 + 0x84); uVar3 = uVar3 + 1) {
      iVar8 = *(int *)(*(int *)(iVar5 + 0x80) + iVar4 + 4);
      if (iVar8 != 0) {
        for (uVar2 = 0; uVar2 < *(uint *)(*(int *)(iVar5 + 0x80) + iVar4); uVar2 = uVar2 + 1) {
          uVar7 = *(uint *)(iVar8 + uVar2 * 8 + 4);
          if (uVar1 <= uVar7) {
            uVar1 = uVar7;
            uVar6 = uVar3;
          }
        }
      }
      iVar4 = iVar4 + 8;
    }
    MonCtrl::ConPrintfMessage(*(char **)(in_r0 + 0x18),DAT_00026dc0 + 0x26db4,uVar6);
  }
  return uVar6;
}


/* 00026dc4 */

/* MprCtrlStillMgr::CalcStillData_JPG(int, int, int, int, unsigned int, unsigned int*, unsigned
   int*) */

int __thiscall
MprCtrlStillMgr::CalcStillData_JPG
          (MprCtrlStillMgr *this,int param_1,int param_2,int param_3,int param_4,uint param_5,
          uint *param_6,uint *param_7)

{
  int iVar1;
  char *pcVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int local_44;
  int local_40;
  int local_3c;
  int local_38;
  int local_34;
  int local_30;
  int local_2c [2];
  
  local_2c[0] = 0;
  local_30 = 0;
  local_34 = 0;
  local_38 = 0;
  local_3c = 0;
  local_40 = 0;
  local_44 = 0;
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x18),DAT_00026f90 + 0x26dd8);
  iVar1 = BackupLib::GetEepData(param_1,'\x04',local_2c);
  if (iVar1 < 0) {
    pcVar2 = *(char **)(this + 0x14);
    iVar6 = DAT_00026f94 + 0x26e0c;
LAB_00026e24:
    MonCtrl::ConPrintfMessage(pcVar2,iVar6,param_1,iVar1);
  }
  else {
    iVar1 = BackupLib::GetEepData(param_2,'\x04',&local_30);
    if (iVar1 < 0) {
      pcVar2 = *(char **)(this + 0x14);
      iVar6 = DAT_00026f98 + 0x26e26;
      param_1 = param_2;
      goto LAB_00026e24;
    }
    iVar1 = BackupLib::GetEepData(DAT_00026f84,'\x04',&local_34);
    if (iVar1 < 0) {
      pcVar2 = *(char **)(this + 0x14);
      iVar6 = DAT_00026f9c + 0x26e46;
LAB_00026e6e:
      MonCtrl::ConPrintfMessage(pcVar2,iVar6,iVar1);
    }
    else {
      iVar6 = IsRecordingSCN(this,param_5);
      if (iVar6 == 0) {
LAB_00026e94:
        iVar1 = BackupLib::GetEepData(DAT_00026f88,'\x02',&local_40);
        if (iVar1 < 0) {
          pcVar2 = *(char **)(this + 0x14);
          iVar6 = DAT_00026fa8 + 0x26eac;
        }
        else {
          iVar1 = BackupLib::GetEepData(DAT_00026f8c,'\x02',&local_44);
          if (-1 < iVar1) {
            iVar3 = Exchg_Byte(this,local_2c[0]);
            local_2c[0] = iVar3;
            iVar4 = Exchg_Byte(this,local_30);
            local_30 = iVar4;
            local_34 = Exchg_Byte(this,local_34);
            if (iVar6 == 0) {
              iVar6 = 0;
              iVar5 = 0;
            }
            else {
              iVar5 = Calc_Align(this,iVar3);
              iVar5 = iVar5 - iVar3;
              iVar6 = Calc_Align(this,iVar4);
              iVar6 = iVar6 - iVar4;
              local_38 = Exchg_Byte(this,local_38);
              local_3c = Exchg_Byte(this,local_3c);
            }
            local_40 = Exchg_Byte(this,local_40);
            local_44 = Exchg_Byte(this,local_44);
            goto LAB_00026f36;
          }
          pcVar2 = *(char **)(this + 0x14);
          iVar6 = DAT_00026fac + 0x26ec2;
        }
      }
      else {
        if ((param_3 != 0) && (iVar1 = BackupLib::GetEepData(param_3,'\x04',&local_38), iVar1 < 0))
        {
          pcVar2 = *(char **)(this + 0x14);
          iVar6 = DAT_00026fa0 + 0x26e70;
          goto LAB_00026e6e;
        }
        if ((param_4 == 0) || (iVar1 = BackupLib::GetEepData(param_4,'\x04',&local_3c), -1 < iVar1))
        goto LAB_00026e94;
        pcVar2 = *(char **)(this + 0x14);
        iVar6 = DAT_00026fa4 + 0x26e94;
      }
      MonCtrl::ConPrintfMessage(pcVar2,iVar6,iVar1);
    }
  }
  iVar6 = 0;
  iVar5 = iVar6;
LAB_00026f36:
  *param_6 = 0;
  *param_7 = 0;
  if (local_2c[0] != 0) {
    *param_6 = local_2c[0] + local_34 + local_38 + local_40 + local_44 + iVar5;
  }
  if (local_30 != 0) {
    *param_7 = iVar6 + local_30 + local_34 + local_3c + local_40 + local_44;
  }
  return iVar1;
}


/* 00026fb0 */

/* MprCtrlStillMgr::CalcStillData_S3(int, int, int, int, unsigned int, unsigned int*, unsigned int*)
    */

int __thiscall
MprCtrlStillMgr::CalcStillData_S3
          (MprCtrlStillMgr *this,int param_1,int param_2,int param_3,int param_4,uint param_5,
          uint *param_6,uint *param_7)

{
  int iVar1;
  char *pcVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int local_44;
  int local_40;
  int local_3c;
  int local_38;
  int local_34;
  int local_30;
  int local_2c [2];
  
  local_2c[0] = 0;
  local_30 = 0;
  local_34 = 0;
  local_38 = 0;
  local_3c = 0;
  local_40 = 0;
  local_44 = 0;
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x18),DAT_000271e0 + 0x26fc4);
  iVar1 = BackupLib::GetEepData(param_1,'\x04',local_2c);
  if (iVar1 < 0) {
    pcVar2 = *(char **)(this + 0x14);
    iVar5 = DAT_000271e4 + 0x26ff8;
LAB_00027010:
    MonCtrl::ConPrintfMessage(pcVar2,iVar5,param_1,iVar1);
  }
  else {
    iVar1 = BackupLib::GetEepData(param_2,'\x04',&local_30);
    if (iVar1 < 0) {
      pcVar2 = *(char **)(this + 0x14);
      iVar5 = DAT_000271e8 + 0x27012;
      param_1 = param_2;
      goto LAB_00027010;
    }
    iVar1 = BackupLib::GetEepData(DAT_000271d4,'\x04',&local_34);
    if (iVar1 < 0) {
      pcVar2 = *(char **)(this + 0x14);
      iVar5 = DAT_000271ec + 0x27036;
LAB_0002705e:
      MonCtrl::ConPrintfMessage(pcVar2,iVar5,iVar1);
    }
    else {
      iVar5 = IsRecordingSCN(this,param_5);
      if (iVar5 == 0) {
LAB_00027082:
        iVar1 = BackupLib::GetEepData(DAT_000271d8,'\x02',&local_40);
        if (iVar1 < 0) {
          pcVar2 = *(char **)(this + 0x14);
          iVar5 = DAT_000271f8 + 0x2709a;
        }
        else {
          iVar1 = BackupLib::GetEepData(DAT_000271dc,'\x02',&local_44);
          if (-1 < iVar1) {
            iVar6 = Exchg_Byte(this,local_2c[0]);
            local_2c[0] = iVar6;
            iVar3 = Exchg_Byte(this,local_30);
            local_30 = iVar3;
            local_34 = Exchg_Byte(this,local_34);
            iVar7 = Calc_Align(this,iVar6);
            iVar7 = iVar7 - iVar6;
            iVar6 = Calc_Align(this,iVar3);
            iVar6 = iVar6 - iVar3;
            if (iVar5 == 0) {
              iVar5 = 0;
              iVar3 = 0;
            }
            else {
              iVar5 = Exchg_Byte(this,local_38);
              local_38 = iVar5;
              iVar4 = Exchg_Byte(this,local_3c);
              iVar3 = 0;
              local_3c = iVar4;
              if (iVar5 != 0) {
                iVar3 = Calc_Align(this,iVar5);
                iVar3 = iVar3 - iVar5;
              }
              iVar5 = 0;
              if (iVar4 != 0) {
                iVar5 = Calc_Align(this,iVar4);
                iVar5 = iVar5 - iVar4;
              }
            }
            local_40 = Exchg_Byte(this,local_40);
            local_44 = Exchg_Byte(this,local_44);
            goto LAB_00027146;
          }
          pcVar2 = *(char **)(this + 0x14);
          iVar5 = DAT_000271fc + 0x270b0;
        }
      }
      else {
        if ((param_3 != 0) && (iVar1 = BackupLib::GetEepData(param_3,'\x04',&local_38), iVar1 < 0))
        {
          pcVar2 = *(char **)(this + 0x14);
          iVar5 = DAT_000271f0 + 0x27060;
          goto LAB_0002705e;
        }
        if ((param_4 == 0) || (iVar1 = BackupLib::GetEepData(param_4,'\x04',&local_3c), -1 < iVar1))
        goto LAB_00027082;
        pcVar2 = *(char **)(this + 0x14);
        iVar5 = DAT_000271f4 + 0x27082;
      }
      MonCtrl::ConPrintfMessage(pcVar2,iVar5,iVar1);
    }
  }
  iVar5 = 0;
  iVar6 = 0;
  iVar7 = 0;
  iVar3 = iVar5;
LAB_00027146:
  *param_6 = 0;
  *param_7 = 0;
  iVar4 = IsRecordingSCN(this,param_5);
  if (iVar4 == 0) {
    if (local_2c[0] != 0) {
      *param_6 = local_40 + local_34 + local_44 + local_2c[0] * 2 + iVar7;
    }
    if (local_30 != 0) {
      *param_7 = local_40 + local_34 + local_44 + local_30 * 2 + iVar6;
    }
  }
  else {
    if (local_2c[0] != 0) {
      *param_6 = iVar3 + local_40 + local_34 + local_44 + (local_2c[0] + local_38 + iVar7) * 2;
    }
    if (local_30 != 0) {
      *param_7 = iVar5 + local_40 + local_34 + local_44 + (iVar6 + local_30 + local_3c) * 2;
    }
  }
  return iVar1;
}


/* 00027200 */

/* MprCtrlStillMgr::CalcStillData_SMV(int, int, int, int, unsigned int, unsigned int*, unsigned
   int*) */

int __thiscall
MprCtrlStillMgr::CalcStillData_SMV
          (MprCtrlStillMgr *this,int param_1,int param_2,int param_3,int param_4,uint param_5,
          uint *param_6,uint *param_7)

{
  int iVar1;
  char *pcVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int local_44;
  int local_40;
  int local_3c;
  int local_38;
  int local_34;
  int local_30;
  int local_2c [2];
  
  local_2c[0] = 0;
  local_30 = 0;
  local_34 = 0;
  local_38 = 0;
  local_3c = 0;
  local_40 = 0;
  local_44 = 0;
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x18),DAT_00027450 + 0x27214);
  iVar1 = BackupLib::GetEepData(param_1,'\x04',local_2c);
  if (iVar1 < 0) {
    pcVar2 = *(char **)(this + 0x14);
    iVar5 = DAT_00027454 + 0x27248;
LAB_00027260:
    MonCtrl::ConPrintfMessage(pcVar2,iVar5,param_1,iVar1);
  }
  else {
    iVar1 = BackupLib::GetEepData(param_2,'\x04',&local_30);
    if (iVar1 < 0) {
      pcVar2 = *(char **)(this + 0x14);
      iVar5 = DAT_00027458 + 0x27262;
      param_1 = param_2;
      goto LAB_00027260;
    }
    iVar1 = BackupLib::GetEepData(DAT_00027444,'\x04',&local_34);
    if (iVar1 < 0) {
      pcVar2 = *(char **)(this + 0x14);
      iVar5 = DAT_0002745c + 0x27286;
LAB_000272ae:
      MonCtrl::ConPrintfMessage(pcVar2,iVar5,iVar1);
    }
    else {
      iVar5 = IsRecordingSCN(this,param_5);
      if (iVar5 == 0) {
LAB_000272d2:
        iVar1 = BackupLib::GetEepData(DAT_00027448,'\x02',&local_40);
        if (iVar1 < 0) {
          pcVar2 = *(char **)(this + 0x14);
          iVar5 = DAT_00027468 + 0x272ea;
        }
        else {
          iVar1 = BackupLib::GetEepData(DAT_0002744c,'\x02',&local_44);
          if (-1 < iVar1) {
            iVar6 = Exchg_Byte(this,local_2c[0]);
            local_2c[0] = iVar6;
            iVar3 = Exchg_Byte(this,local_30);
            local_30 = iVar3;
            local_34 = Exchg_Byte(this,local_34);
            iVar7 = Calc_Align(this,iVar6);
            iVar7 = iVar7 - iVar6;
            iVar6 = Calc_Align(this,iVar3);
            iVar6 = iVar6 - iVar3;
            if (iVar5 == 0) {
              iVar5 = 0;
              iVar3 = 0;
            }
            else {
              iVar5 = Exchg_Byte(this,local_38);
              local_38 = iVar5;
              iVar4 = Exchg_Byte(this,local_3c);
              iVar3 = 0;
              local_3c = iVar4;
              if (iVar5 != 0) {
                iVar3 = Calc_Align(this,iVar5);
                iVar3 = iVar3 - iVar5;
              }
              iVar5 = 0;
              if (iVar4 != 0) {
                iVar5 = Calc_Align(this,iVar4);
                iVar5 = iVar5 - iVar4;
              }
            }
            local_40 = Exchg_Byte(this,local_40);
            local_44 = Exchg_Byte(this,local_44);
            goto LAB_00027396;
          }
          pcVar2 = *(char **)(this + 0x14);
          iVar5 = DAT_0002746c + 0x27300;
        }
      }
      else {
        if ((param_3 != 0) && (iVar1 = BackupLib::GetEepData(param_3,'\x04',&local_38), iVar1 < 0))
        {
          pcVar2 = *(char **)(this + 0x14);
          iVar5 = DAT_00027460 + 0x272b0;
          goto LAB_000272ae;
        }
        if ((param_4 == 0) || (iVar1 = BackupLib::GetEepData(param_4,'\x04',&local_3c), -1 < iVar1))
        goto LAB_000272d2;
        pcVar2 = *(char **)(this + 0x14);
        iVar5 = DAT_00027464 + 0x272d2;
      }
      MonCtrl::ConPrintfMessage(pcVar2,iVar5,iVar1);
    }
  }
  iVar5 = 0;
  iVar6 = 0;
  iVar7 = 0;
  iVar3 = iVar5;
LAB_00027396:
  *param_6 = 0;
  *param_7 = 0;
  iVar4 = IsRecordingSCN(this,param_5);
  if (iVar4 == 0) {
    if (local_2c[0] != 0) {
      *param_6 = iVar7 * 0xe + local_40 + local_34 + local_44 + local_2c[0] * 0xf;
    }
    if (local_30 != 0) {
      *param_7 = iVar6 * 0xe + local_40 + local_34 + local_44 + local_30 * 0xf;
    }
  }
  else {
    if (local_2c[0] != 0) {
      *param_6 = iVar3 * 0xe + local_40 + local_34 + local_44 +
                 (iVar7 + local_2c[0] + local_38) * 0xf;
    }
    if (local_30 != 0) {
      *param_7 = iVar5 * 0xe + local_40 + local_34 + local_44 + (iVar6 + local_30 + local_3c) * 0xf;
    }
  }
  return iVar1;
}


/* 00027470 */

/* MprCtrlStillMgr::CalcStillData_RAW(int, int, int, unsigned int*, unsigned int*) */

int __thiscall
MprCtrlStillMgr::CalcStillData_RAW
          (MprCtrlStillMgr *this,int param_1,int param_2,int param_3,uint *param_4,uint *param_5)

{
  int iVar1;
  char *pcVar2;
  int iVar3;
  int iVar4;
  int local_48;
  int local_44;
  int local_40;
  int local_3c;
  int local_38;
  int local_34;
  int local_30;
  int local_2c [2];
  
  iVar4 = 0;
  local_2c[0] = 0;
  local_30 = 0;
  local_34 = 0;
  local_38 = 0;
  local_3c = 0;
  local_40 = 0;
  local_44 = 0;
  local_48 = 0;
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x18),DAT_0002762c + 0x27484);
  iVar1 = BackupLib::GetEepData(param_1,'\x04',local_2c);
  if (iVar1 < 0) {
    pcVar2 = *(char **)(this + 0x14);
    iVar3 = DAT_00027630 + 0x274bc;
  }
  else {
    iVar1 = BackupLib::GetEepData(DAT_00027618,'\x04',&local_30);
    if (-1 < iVar1) {
      iVar1 = BackupLib::GetEepData(param_2,'\x04',&local_34);
      if (iVar1 < 0) {
        pcVar2 = *(char **)(this + 0x14);
        iVar3 = DAT_00027638 + 0x274f4;
      }
      else {
        iVar1 = BackupLib::GetEepData(param_3,'\x04',&local_38);
        if (-1 < iVar1) {
          iVar1 = BackupLib::GetEepData(DAT_0002761c,'\x02',&local_3c);
          if (iVar1 < 0) {
            pcVar2 = *(char **)(this + 0x14);
            iVar3 = DAT_00027640 + 0x2752c;
          }
          else {
            iVar1 = BackupLib::GetEepData(DAT_00027620,'\x02',&local_40);
            if (iVar1 < 0) {
              pcVar2 = *(char **)(this + 0x14);
              iVar3 = DAT_00027644 + 0x27544;
            }
            else {
              iVar1 = BackupLib::GetEepData(DAT_00027624,'\x02',&local_44);
              if (iVar1 < 0) {
                pcVar2 = *(char **)(this + 0x14);
                iVar3 = DAT_00027648 + 0x2755a;
              }
              else {
                iVar1 = BackupLib::GetEepData(DAT_00027628,'\x02',&local_48);
                if (-1 < iVar1) {
                  local_2c[0] = Exchg_Byte(this,local_2c[0]);
                  local_30 = Exchg_Byte(this,local_30);
                  iVar3 = Exchg_Byte(this,local_34);
                  local_34 = iVar3;
                  local_38 = Exchg_Byte(this,local_38);
                  iVar4 = Calc_Align(this,iVar3);
                  iVar4 = iVar4 - iVar3;
                  local_3c = Exchg_Byte(this,local_3c);
                  local_40 = Exchg_Byte(this,local_40);
                  local_44 = Exchg_Byte(this,local_44);
                  local_48 = Exchg_Byte(this,local_48);
                  goto LAB_000275cc;
                }
                pcVar2 = *(char **)(this + 0x14);
                iVar3 = DAT_0002764c + 0x27570;
              }
            }
          }
          goto LAB_000274d2;
        }
        pcVar2 = *(char **)(this + 0x14);
        iVar3 = DAT_0002763c + 0x2750e;
        param_2 = param_3;
      }
      MonCtrl::ConPrintfMessage(pcVar2,iVar3,param_2,iVar1);
      goto LAB_000275cc;
    }
    pcVar2 = *(char **)(this + 0x14);
    iVar3 = DAT_00027634 + 0x274d4;
  }
LAB_000274d2:
  MonCtrl::ConPrintfMessage(pcVar2,iVar3,iVar1);
LAB_000275cc:
  *param_4 = 0;
  *param_5 = 0;
  if (local_2c[0] != 0) {
    *param_4 = iVar4 + local_34 + local_3c + local_40 + local_44 + local_48 + local_2c[0] + local_30
    ;
    *param_5 = local_40 + local_3c + local_44 + local_48 + local_38 + local_2c[0] + local_30;
  }
  return iVar1;
}


/* 00027650 */

/* MprCtrlStillMgr::GetStillDataInfo(int, int, int, int, int, int, MprCtrlStill::StillDataInfo*) */

int __thiscall
MprCtrlStillMgr::GetStillDataInfo
          (MprCtrlStillMgr *this,int param_1,int param_2,int param_3,int param_4,int param_5,
          int param_6,StillDataInfo *param_7)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  uint local_3c;
  uint local_38;
  int local_34;
  int local_30;
  int local_2c [2];
  
  local_2c[0] = 0;
  local_30 = 0;
  local_34 = 0;
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x18),DAT_00027800 + 0x2766a);
  switch(param_1) {
  case 0:
    iVar2 = DAT_00027804 + 0x27692;
    iVar1 = DAT_00027808 + 0x27694;
    break;
  case 1:
    iVar3 = param_2 * 3;
    iVar2 = DAT_0002780c + 0x276a2;
    iVar1 = DAT_00027810 + 0x276a4;
    goto LAB_000276be;
  case 2:
  case 3:
    iVar2 = DAT_00027814 + 0x276ac;
    iVar1 = DAT_00027818 + 0x276ae;
    break;
  default:
    uVar4 = 0;
    goto LAB_000276cc;
  }
  iVar3 = param_3 * 6 + param_2 * 0x1e + param_5 * 3;
LAB_000276be:
  uVar4 = *(uint *)(iVar2 + *(int *)(iVar1 + (param_4 + iVar3) * 8 + 4) * 0x10);
LAB_000276cc:
  iVar1 = BackupLib::GetEepData(uVar4,'\x04',local_2c);
  if (iVar1 < 0) {
    MonCtrl::ConPrintfMessage(*(char **)(this + 0x14),DAT_0002781c + 0x276e8,uVar4,iVar1);
  }
  else {
    iVar1 = BackupLib::GetEepData(DAT_000277f8,'\x04',&local_30);
    if (-1 < iVar1) {
      if (param_6 == 0xff) {
        local_34 = 0;
        uVar5 = 0;
      }
      else {
        uVar5 = *(uint *)(DAT_00027824 + 0x2771e + param_6 * 0x10);
        iVar1 = BackupLib::GetEepData(uVar5,'\x04',&local_34);
        if (iVar1 < 0) {
          MonCtrl::ConPrintfMessage(*(char **)(this + 0x14),DAT_00027828 + 0x27738,iVar1);
        }
      }
      goto LAB_00027742;
    }
    MonCtrl::ConPrintfMessage(*(char **)(this + 0x14),DAT_00027820 + 0x27706,iVar1);
  }
  uVar5 = 0;
LAB_00027742:
  iVar2 = Exchg_Byte(this,local_2c[0]);
  local_2c[0] = iVar2;
  local_30 = Exchg_Byte(this,local_30);
  if (param_6 != 0xff) {
    local_34 = Exchg_Byte(this,local_34);
  }
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x18),DAT_0002782c + 0x27774,uVar4,iVar2);
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x18),DAT_00027830 + 0x2777e,DAT_000277f8,local_30);
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x18),DAT_00027834 + 0x27790,uVar5,local_34);
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x18),DAT_00027838 + 0x2779a);
  *(int *)param_7 = local_2c[0];
  *(int *)(param_7 + 4) = local_30;
  *(int *)(param_7 + 8) = local_34;
  if (param_1 == 3) {
    local_38 = 0;
    local_3c = 0;
    CalcStillData_RAW(this,DAT_000277fc,*(int *)(DAT_0002783c + 0x277c2 + param_3 * 0x10),
                      *(int *)(DAT_0002783c + 0x277c2 + param_3 * 0x10 + 8),&local_38,&local_3c);
    *(uint *)param_7 = *(int *)param_7 + local_38;
  }
  return iVar1;
}


/* 00027840 */

/* MprCtrlStillMgr::CreateStillData() */

void __thiscall MprCtrlStillMgr::CreateStillData(MprCtrlStillMgr *this)

{
  int *piVar1;
  int iVar2;
  uint *puVar3;
  int iVar4;
  undefined4 *puVar5;
  void *pvVar6;
  int *piVar7;
  int extraout_r1;
  int extraout_r1_00;
  int extraout_r1_01;
  int extraout_r1_02;
  int extraout_r1_03;
  int extraout_r1_04;
  int extraout_r1_05;
  int extraout_r1_06;
  int extraout_r1_07;
  int extraout_r1_08;
  int extraout_r1_09;
  int extraout_r1_10;
  int extraout_r1_11;
  int extraout_r1_12;
  int iVar8;
  int extraout_r1_13;
  int extraout_r1_14;
  int extraout_r1_15;
  int extraout_r1_16;
  int extraout_r1_17;
  int extraout_r1_18;
  int extraout_r1_19;
  int extraout_r1_20;
  int extraout_r1_21;
  int extraout_r1_22;
  int extraout_r1_23;
  int extraout_r1_24;
  int extraout_r1_25;
  undefined4 uVar9;
  int *piVar10;
  undefined4 *puVar11;
  undefined4 uVar12;
  undefined4 uVar13;
  int iVar14;
  uint uVar15;
  int iVar16;
  int *piVar17;
  int iVar18;
  uint uVar19;
  int iVar20;
  int iVar21;
  uint uVar22;
  int iVar23;
  int iVar24;
  int *local_3c;
  int *local_34;
  uint local_30;
  uint local_2c [2];
  
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x18),DAT_00027ce0 + 0x27852);
  piVar7 = (int *)(DAT_00027ce4 + 0x27862);
  iVar16 = 0;
  iVar20 = 0;
  local_2c[0] = 0;
  local_30 = 0;
  piVar17 = piVar7;
  iVar4 = 0;
  do {
    iVar14 = iVar4;
    iVar4 = DAT_00027ce8;
    iVar2 = GetStillSizeRow(this,iVar20 * 5 + iVar16);
    CalcStillData_JPG(this,*piVar17,piVar17[2],*(int *)(DAT_00027cec + 0x2788c + iVar16 * 0x10),
                      *(int *)(DAT_00027cec + 0x2788c + iVar16 * 0x10 + 8),*(uint *)(iVar2 + 4),
                      local_2c,&local_30);
    *(undefined4 *)(iVar4 + 0x2788a + iVar14 * 8) = 1;
    puVar3 = operator_new__(8);
    *(uint **)(iVar4 + 0x2788a + iVar14 * 8 + 4) = puVar3;
    *puVar3 = local_2c[0];
    puVar3[1] = local_30;
    __aeabi_idivmod(iVar14,3);
    if (extraout_r1 == 2) {
      iVar16 = iVar16 + 1;
    }
    __aeabi_idivmod(iVar14,0xf);
    if (extraout_r1_00 == 0xe) {
      iVar20 = iVar20 + 1;
      iVar16 = 0;
    }
    piVar17 = piVar17 + 4;
    iVar4 = iVar14 + 1;
  } while (iVar14 + 1 != 0x3c);
  iVar14 = iVar14 + -0x3b;
  piVar10 = (int *)(DAT_00027cf0 + 0x27900);
  piVar17 = piVar10;
  iVar4 = iVar14;
  iVar20 = iVar14;
  do {
    iVar16 = iVar4;
    iVar4 = GetStillSizeRow(this,iVar14 + 0x14 + iVar20 * 5);
    iVar2 = DAT_00027cf8 + 0x27934;
    CalcStillData_JPG(this,*piVar17,piVar17[2],*(int *)(DAT_00027cf4 + 0x2792a + iVar14 * 0x10),
                      *(int *)(DAT_00027cf4 + 0x2792a + iVar14 * 0x10 + 8),*(uint *)(iVar4 + 4),
                      local_2c,&local_30);
    *(undefined4 *)(iVar2 + iVar16 * 8) = 1;
    puVar3 = operator_new__(8);
    *(uint **)(iVar2 + iVar16 * 8 + 4) = puVar3;
    *puVar3 = local_2c[0];
    puVar3[1] = local_30;
    __aeabi_idivmod(iVar16,3);
    if (extraout_r1_01 == 2) {
      iVar14 = iVar14 + 1;
    }
    __aeabi_idivmod(iVar16,0xf);
    if (extraout_r1_02 == 0xe) {
      iVar20 = iVar20 + 1;
      iVar14 = 0;
    }
    piVar17 = piVar17 + 4;
    iVar4 = iVar16 + 1;
  } while (iVar16 + 1 != 0x3c);
  iVar16 = iVar16 + -0x3b;
  iVar20 = iVar16;
  iVar4 = iVar16;
  do {
    iVar14 = DAT_00027cfc + 0x279aa;
    *(undefined4 *)(iVar14 + iVar16) = 2;
    iVar14 = iVar14 + iVar16;
    puVar5 = operator_new__(0x10);
    puVar11 = *(undefined4 **)(DAT_00027d00 + iVar16 + 0x279c4);
    uVar9 = *puVar11;
    uVar12 = puVar11[1];
    *(undefined4 **)(iVar14 + 4) = puVar5;
    *puVar5 = uVar9;
    iVar2 = DAT_00027d04;
    puVar5[1] = uVar12;
    CalcStillData_RAW(this,DAT_00027cd8,*(int *)(iVar2 + 0x279d6 + iVar4 * 0x10),
                      *(int *)(iVar2 + 0x279d6 + iVar4 * 0x10 + 8),local_2c,&local_30);
    iVar2 = *(int *)(iVar14 + 4);
    *(uint *)(iVar2 + 8) = local_2c[0];
    *(uint *)(iVar2 + 0xc) = local_30;
    __aeabi_idivmod(iVar20,3);
    if (extraout_r1_03 == 2) {
      iVar4 = iVar4 + 1;
    }
    __aeabi_idivmod(iVar20,0xf);
    iVar20 = iVar20 + 1;
    iVar16 = iVar16 + 8;
    if (extraout_r1_04 == 0xe) {
      iVar4 = 0;
    }
  } while (iVar20 != 0x3c);
  iVar20 = 0;
  iVar4 = 0;
  iVar16 = 0;
  do {
    iVar14 = DAT_00027d08 + 0x27a32;
    *(undefined4 *)(iVar14 + iVar20) = 2;
    iVar14 = iVar14 + iVar20;
    puVar5 = operator_new__(0x10);
    puVar11 = *(undefined4 **)(DAT_00027d0c + iVar20 + 0x27a4c);
    uVar9 = *puVar11;
    uVar12 = puVar11[1];
    *(undefined4 **)(iVar14 + 4) = puVar5;
    *puVar5 = uVar9;
    iVar2 = DAT_00027d10;
    puVar5[1] = uVar12;
    CalcStillData_RAW(this,DAT_00027cdc,*(int *)(iVar2 + 0x27a5e + iVar16 * 0x10),
                      *(int *)(iVar2 + 0x27a5e + iVar16 * 0x10 + 8),local_2c,&local_30);
    iVar2 = *(int *)(iVar14 + 4);
    *(uint *)(iVar2 + 8) = local_2c[0];
    *(uint *)(iVar2 + 0xc) = local_30;
    __aeabi_idivmod(iVar4,3);
    if (extraout_r1_05 == 2) {
      iVar16 = iVar16 + 1;
    }
    __aeabi_idivmod(iVar4,0xf);
    iVar4 = iVar4 + 1;
    iVar20 = iVar20 + 8;
    if (extraout_r1_06 == 0xe) {
      iVar16 = 0;
    }
  } while (iVar4 != 0x3c);
  iVar20 = 0;
  iVar4 = 0;
  iVar16 = 0;
  do {
    iVar2 = DAT_00027d18 + 0x27ac8;
    CalcStillData_RAW(this,DAT_00027cd8,*(int *)(DAT_00027d14 + 0x27ac0 + iVar16 * 0x10),
                      *(int *)(DAT_00027d14 + 0x27ac0 + iVar16 * 0x10 + 8),local_2c,&local_30);
    *(undefined4 *)(iVar2 + iVar20) = 1;
    puVar3 = operator_new__(8);
    *(uint **)(iVar2 + iVar20 + 4) = puVar3;
    *puVar3 = local_2c[0];
    puVar3[1] = local_30;
    __aeabi_idivmod(iVar4,3);
    if (extraout_r1_07 == 2) {
      iVar16 = iVar16 + 1;
    }
    __aeabi_idivmod(iVar4,0xf);
    iVar4 = iVar4 + 1;
    iVar20 = iVar20 + 8;
    if (extraout_r1_08 == 0xe) {
      iVar16 = 0;
    }
  } while (iVar4 != 0xf);
  iVar20 = 0;
  iVar4 = 0;
  iVar16 = 0;
  do {
    iVar2 = DAT_00027d20 + 0x27b3c;
    CalcStillData_RAW(this,DAT_00027cdc,*(int *)(DAT_00027d1c + 0x27b34 + iVar16 * 0x10),
                      *(int *)(DAT_00027d1c + 0x27b34 + iVar16 * 0x10 + 8),local_2c,&local_30);
    *(undefined4 *)(iVar2 + iVar20) = 1;
    puVar3 = operator_new__(8);
    *(uint **)(iVar2 + iVar20 + 4) = puVar3;
    *puVar3 = local_2c[0];
    puVar3[1] = local_30;
    __aeabi_idivmod(iVar4,3);
    if (extraout_r1_09 == 2) {
      iVar16 = iVar16 + 1;
    }
    __aeabi_idivmod(iVar4,0xf);
    iVar4 = iVar4 + 1;
    iVar20 = iVar20 + 8;
    if (extraout_r1_10 == 0xe) {
      iVar16 = 0;
    }
  } while (iVar4 != 0xf);
  iVar20 = 0;
  iVar4 = 0;
  iVar16 = 0;
  local_34 = (int *)(DAT_00027d24 + 0x27b9c);
  piVar17 = local_34;
  do {
    iVar2 = GetStillSizeRow(this,iVar16 + 0x28);
    iVar14 = DAT_00027d2c + 0x27bc0;
    CalcStillData_JPG(this,*piVar17,piVar17[2],*(int *)(DAT_00027d28 + 0x27bb6 + iVar16 * 0x10),
                      *(int *)(DAT_00027d28 + 0x27bb6 + iVar16 * 0x10 + 8),*(uint *)(iVar2 + 4),
                      local_2c,&local_30);
    *(undefined4 *)(iVar14 + iVar20) = 1;
    puVar3 = operator_new__(8);
    *(uint **)(iVar14 + iVar20 + 4) = puVar3;
    *puVar3 = local_2c[0];
    puVar3[1] = local_30;
    __aeabi_idivmod(iVar4,3);
    iVar4 = iVar4 + 1;
    if (extraout_r1_11 == 2) {
      iVar16 = iVar16 + 1;
    }
    piVar17 = piVar17 + 4;
    iVar20 = iVar20 + 8;
  } while (iVar4 != 0x18);
  iVar20 = 0;
  iVar4 = 0;
  iVar16 = 0;
  local_3c = (int *)(DAT_00027d30 + 0x27c20);
  piVar17 = local_3c;
  do {
    iVar2 = GetStillSizeRow(this,iVar16 + 0x30);
    iVar14 = DAT_00027d38 + 0x27c44;
    CalcStillData_JPG(this,*piVar17,piVar17[2],*(int *)(DAT_00027d34 + 0x27c3a + iVar16 * 0x10),
                      *(int *)(DAT_00027d34 + 0x27c3a + iVar16 * 0x10 + 8),*(uint *)(iVar2 + 4),
                      local_2c,&local_30);
    *(undefined4 *)(iVar14 + iVar20) = 1;
    puVar3 = operator_new__(8);
    *(uint **)(iVar14 + iVar20 + 4) = puVar3;
    *puVar3 = local_2c[0];
    puVar3[1] = local_30;
    __aeabi_idivmod(iVar4,3);
    iVar4 = iVar4 + 1;
    if (extraout_r1_12 == 2) {
      iVar16 = iVar16 + 1;
    }
    piVar17 = piVar17 + 4;
    iVar20 = iVar20 + 8;
  } while (iVar4 != 0x18);
  iVar4 = 0;
  iVar16 = 0;
  piVar17 = (int *)(DAT_00027d3c + 0x27ca4);
  iVar20 = 0;
  do {
    iVar2 = GetStillSizeRow(this,iVar16 + 0x38);
    iVar21 = DAT_00027d40 + 0x27cb6;
    *(undefined4 *)(iVar21 + iVar4) = 2;
    iVar21 = iVar21 + iVar4;
    pvVar6 = operator_new__(0x10);
    iVar14 = *(int *)(DAT_00027d44 + 0x27ccc + iVar16 * 0x10);
    iVar24 = *(int *)(DAT_00027d44 + 0x27ccc + iVar16 * 0x10 + 8);
    iVar8 = *piVar17;
    *(void **)(iVar21 + 4) = pvVar6;
    CalcStillData_JPG(this,iVar8,piVar17[2],iVar14,iVar24,*(uint *)(iVar2 + 4),local_2c,&local_30);
    puVar3 = *(uint **)(iVar21 + 4);
    *puVar3 = local_2c[0];
    puVar3[1] = local_30;
    CalcStillData_S3(this,*piVar17,piVar17[2],iVar14,iVar24,*(uint *)(iVar2 + 4),local_2c,&local_30)
    ;
    iVar2 = *(int *)(iVar21 + 4);
    iVar14 = iVar20 + 1;
    *(uint *)(iVar2 + 8) = local_2c[0];
    *(uint *)(iVar2 + 0xc) = local_30;
    __aeabi_idivmod(iVar20,3);
    if (extraout_r1_13 == 2) {
      iVar16 = iVar16 + 1;
    }
    iVar4 = iVar4 + 8;
    piVar17 = piVar17 + 4;
    iVar20 = iVar14;
  } while (iVar14 != 9);
  iVar4 = 0;
  iVar16 = 0;
  piVar17 = (int *)(DAT_000281ac + 0x27dda);
  iVar20 = 0;
  do {
    iVar2 = GetStillSizeRow(this,iVar16 + 0x3b);
    iVar21 = DAT_000281b0 + 0x27dec;
    *(undefined4 *)(iVar21 + iVar4) = 2;
    iVar21 = iVar21 + iVar4;
    pvVar6 = operator_new__(0x10);
    iVar14 = *(int *)(DAT_000281b4 + 0x27e02 + iVar16 * 0x10);
    iVar24 = *(int *)(DAT_000281b4 + 0x27e02 + iVar16 * 0x10 + 8);
    iVar8 = piVar17[2];
    *(void **)(iVar21 + 4) = pvVar6;
    CalcStillData_JPG(this,*piVar17,iVar8,iVar14,iVar24,*(uint *)(iVar2 + 4),local_2c,&local_30);
    puVar3 = *(uint **)(iVar21 + 4);
    iVar8 = *piVar17;
    *puVar3 = local_2c[0];
    puVar3[1] = local_30;
    CalcStillData_S3(this,iVar8,piVar17[2],iVar14,iVar24,*(uint *)(iVar2 + 4),local_2c,&local_30);
    iVar2 = *(int *)(iVar21 + 4);
    iVar14 = iVar20 + 1;
    *(uint *)(iVar2 + 8) = local_2c[0];
    *(uint *)(iVar2 + 0xc) = local_30;
    __aeabi_idivmod(iVar20,3);
    if (extraout_r1_14 == 2) {
      iVar16 = iVar16 + 1;
    }
    iVar4 = iVar4 + 8;
    piVar17 = piVar17 + 4;
    iVar20 = iVar14;
  } while (iVar14 != 9);
  iVar4 = 0;
  iVar16 = 0;
  iVar20 = 0;
  do {
    iVar18 = DAT_000281b8 + 0x27ea2;
    *(undefined4 *)(iVar18 + iVar4) = 4;
    iVar18 = iVar18 + iVar4;
    puVar5 = operator_new__(0x20);
    puVar11 = *(undefined4 **)(DAT_000281bc + iVar4 + 0x27eb8);
    uVar9 = *puVar11;
    *(undefined4 **)(iVar18 + 4) = puVar5;
    *puVar5 = uVar9;
    puVar5[1] = puVar11[1];
    uVar9 = puVar11[1];
    puVar5[4] = *puVar11;
    puVar5[5] = uVar9;
    iVar2 = GetStillSizeRow(this,iVar16 + 0x28);
    iVar14 = *local_34;
    iVar21 = local_34[2];
    iVar8 = *(int *)(DAT_000281c0 + 0x27ee2 + iVar16 * 0x10);
    iVar23 = *(int *)(DAT_000281c0 + 0x27ee2 + iVar16 * 0x10 + 8);
    CalcStillData_S3(this,iVar14,iVar21,iVar8,iVar23,*(uint *)(iVar2 + 4),local_2c,&local_30);
    iVar24 = *(int *)(iVar18 + 4);
    *(uint *)(iVar24 + 8) = local_2c[0];
    *(uint *)(iVar24 + 0xc) = local_30;
    CalcStillData_SMV(this,iVar14,iVar21,iVar8,iVar23,*(uint *)(iVar2 + 4),local_2c,&local_30);
    iVar2 = *(int *)(iVar18 + 4);
    iVar14 = iVar20 + 1;
    *(uint *)(iVar2 + 0x18) = local_2c[0];
    *(uint *)(iVar2 + 0x1c) = local_30;
    __aeabi_idivmod(iVar20,3);
    if (extraout_r1_15 == 2) {
      iVar16 = iVar16 + 1;
    }
    local_34 = local_34 + 4;
    iVar4 = iVar4 + 8;
    iVar20 = iVar14;
  } while (iVar14 != 9);
  iVar4 = 0;
  iVar16 = 0;
  iVar20 = 0;
  do {
    iVar18 = DAT_000281c4 + 0x27f84;
    *(undefined4 *)(iVar18 + iVar4) = 4;
    iVar18 = iVar18 + iVar4;
    puVar5 = operator_new__(0x20);
    puVar11 = *(undefined4 **)(DAT_000281c8 + iVar4 + 0x27f9a);
    uVar9 = *puVar11;
    *(undefined4 **)(iVar18 + 4) = puVar5;
    *puVar5 = uVar9;
    puVar5[1] = puVar11[1];
    uVar9 = puVar11[1];
    puVar5[4] = *puVar11;
    puVar5[5] = uVar9;
    iVar2 = GetStillSizeRow(this,iVar16 + 0x30);
    iVar21 = *local_3c;
    iVar14 = local_3c[2];
    iVar8 = *(int *)(DAT_000281cc + 0x27fcc + iVar16 * 0x10);
    iVar23 = *(int *)(DAT_000281cc + 0x27fcc + iVar16 * 0x10 + 8);
    CalcStillData_S3(this,iVar21,iVar14,iVar8,iVar23,*(uint *)(iVar2 + 4),local_2c,&local_30);
    iVar24 = *(int *)(iVar18 + 4);
    *(uint *)(iVar24 + 8) = local_2c[0];
    *(uint *)(iVar24 + 0xc) = local_30;
    CalcStillData_SMV(this,iVar21,iVar14,iVar8,iVar23,*(uint *)(iVar2 + 4),local_2c,&local_30);
    iVar2 = *(int *)(iVar18 + 4);
    iVar14 = iVar20 + 1;
    *(uint *)(iVar2 + 0x18) = local_2c[0];
    *(uint *)(iVar2 + 0x1c) = local_30;
    __aeabi_idivmod(iVar20,3);
    if (extraout_r1_16 == 2) {
      iVar16 = iVar16 + 1;
    }
    iVar4 = iVar4 + 8;
    local_3c = local_3c + 4;
    iVar20 = iVar14;
  } while (iVar14 != 9);
  iVar16 = 0;
  iVar20 = 0;
  piVar17 = (int *)(DAT_000281d0 + 0x28060);
  iVar4 = 0;
  do {
    iVar2 = iVar4;
    iVar4 = GetStillSizeRow(this,iVar16 + 0x40 + iVar20 * 5);
    iVar14 = DAT_000281d8 + 0x28084;
    CalcStillData_JPG(this,*piVar17,piVar17[2],*(int *)(DAT_000281d4 + 0x2807c + iVar16 * 0x10),
                      *(int *)(DAT_000281d4 + 0x2807c + iVar16 * 0x10 + 8),*(uint *)(iVar4 + 4),
                      local_2c,&local_30);
    *(undefined4 *)(iVar14 + iVar2 * 8) = 1;
    puVar3 = operator_new__(8);
    *(uint **)(iVar14 + iVar2 * 8 + 4) = puVar3;
    *puVar3 = local_2c[0];
    puVar3[1] = local_30;
    __aeabi_idivmod(iVar2,3);
    if (extraout_r1_17 == 2) {
      iVar16 = iVar16 + 1;
    }
    __aeabi_idivmod(iVar2,0xf);
    if (extraout_r1_18 == 0xe) {
      iVar20 = iVar20 + 1;
      iVar16 = 0;
    }
    piVar17 = piVar17 + 4;
    iVar4 = iVar2 + 1;
  } while (iVar2 + 1 != 0x2d);
  iVar2 = iVar2 + -0x2c;
  piVar17 = (int *)(DAT_000281dc + 0x280f8);
  iVar4 = iVar2;
  iVar20 = iVar2;
  do {
    iVar16 = iVar4;
    iVar4 = GetStillSizeRow(this,iVar2 + 0x4f + iVar20 * 5);
    iVar14 = DAT_000281e4 + 0x2811e;
    CalcStillData_JPG(this,*piVar17,piVar17[2],*(int *)(DAT_000281e0 + 0x28114 + iVar2 * 0x10),
                      *(int *)(DAT_000281e0 + 0x28114 + iVar2 * 0x10 + 8),*(uint *)(iVar4 + 4),
                      local_2c,&local_30);
    *(undefined4 *)(iVar14 + iVar16 * 8) = 1;
    puVar3 = operator_new__(8);
    *(uint **)(iVar14 + iVar16 * 8 + 4) = puVar3;
    *puVar3 = local_2c[0];
    puVar3[1] = local_30;
    __aeabi_idivmod(iVar16,3);
    if (extraout_r1_19 == 2) {
      iVar2 = iVar2 + 1;
    }
    __aeabi_idivmod(iVar16,0xf);
    if (extraout_r1_20 == 0xe) {
      iVar20 = iVar20 + 1;
      iVar2 = 0;
    }
    piVar17 = piVar17 + 4;
    iVar4 = iVar16 + 1;
  } while (iVar16 + 1 != 0x2d);
  uVar15 = iVar16 - 0x2c;
  piVar17 = (int *)(DAT_000281e8 + 0x28190);
  uVar19 = uVar15;
  uVar22 = uVar15;
  do {
    iVar20 = GetStillSizeRow(this,uVar19 + 0x60);
    if (uVar19 < 2) {
      uVar22 = 2;
    }
    else if (uVar19 == 2) {
      uVar22 = 1;
    }
    iVar4 = DAT_0002854c + 0x2820a;
    CalcStillData_JPG(this,*piVar17,piVar17[2],*(int *)(DAT_00028548 + 0x28202 + uVar22 * 0x10),
                      *(int *)(DAT_00028548 + 0x28202 + uVar22 * 0x10 + 8),*(uint *)(iVar20 + 4),
                      local_2c,&local_30);
    *(undefined4 *)(iVar4 + uVar15 * 8) = 1;
    puVar3 = operator_new__(8);
    *(uint **)(iVar4 + uVar15 * 8 + 4) = puVar3;
    *puVar3 = local_2c[0];
    puVar3[1] = local_30;
    __aeabi_idivmod(uVar15,3);
    if (extraout_r1_21 == 2) {
      uVar19 = uVar19 + 1;
    }
    uVar15 = uVar15 + 1;
    piVar17 = piVar17 + 4;
  } while (uVar15 != 9);
  iVar4 = GetStillSizeRow(this,0x3e);
  piVar17 = (int *)(DAT_00028550 + 0x2826c);
  iVar20 = 0;
  do {
    iVar16 = iVar20;
    iVar20 = *piVar17;
    iVar2 = DAT_00028554 + 0x2827e;
    piVar1 = piVar17 + 2;
    piVar17 = piVar17 + 4;
    CalcStillData_JPG(this,iVar20,*piVar1,DAT_00028544,DAT_00028540,*(uint *)(iVar4 + 4),local_2c,
                      &local_30);
    *(undefined4 *)(iVar2 + iVar16) = 1;
    puVar3 = operator_new__(8);
    *(uint **)(iVar2 + iVar16 + 4) = puVar3;
    *puVar3 = local_2c[0];
    puVar3[1] = local_30;
    iVar20 = iVar16 + 8;
  } while (iVar16 + 8 != 0x18);
  iVar4 = GetStillSizeRow(this,0x3f);
  piVar17 = (int *)(DAT_00028558 + 0x282cc);
  iVar20 = iVar16 + -0x10;
  do {
    iVar16 = iVar20;
    piVar1 = piVar17 + 2;
    iVar2 = DAT_0002855c + 0x282e0;
    iVar20 = *piVar17;
    piVar17 = piVar17 + 4;
    CalcStillData_JPG(this,iVar20,*piVar1,DAT_00028544,DAT_00028540,*(uint *)(iVar4 + 4),local_2c,
                      &local_30);
    *(undefined4 *)(iVar2 + iVar16) = 1;
    puVar3 = operator_new__(8);
    *(uint **)(iVar2 + iVar16 + 4) = puVar3;
    *puVar3 = local_2c[0];
    puVar3[1] = local_30;
    iVar20 = iVar16 + 8;
  } while (iVar16 + 8 != 0x18);
  iVar20 = GetStillSizeRow(this,0x5e);
  iVar16 = iVar16 + -0x10;
  piVar17 = (int *)(DAT_00028560 + 0x28326);
  do {
    iVar2 = DAT_00028564 + 0x2833c;
    iVar4 = *piVar17;
    piVar1 = piVar17 + 2;
    piVar17 = piVar17 + 4;
    CalcStillData_JPG(this,iVar4,*piVar1,0,0,*(uint *)(iVar20 + 4),local_2c,&local_30);
    *(undefined4 *)(iVar2 + iVar16) = 1;
    puVar3 = operator_new__(8);
    iVar2 = iVar2 + iVar16;
    iVar16 = iVar16 + 8;
    *(uint **)(iVar2 + 4) = puVar3;
    *puVar3 = local_2c[0];
    puVar3[1] = local_30;
  } while (iVar16 != 0x18);
  iVar20 = GetStillSizeRow(this,0x5f);
  iVar4 = 0;
  piVar17 = (int *)(DAT_00028568 + 0x28388);
  do {
    iVar14 = 0;
    iVar2 = DAT_0002856c + 0x2839c;
    iVar16 = *piVar17;
    piVar1 = piVar17 + 2;
    piVar17 = piVar17 + 4;
    CalcStillData_JPG(this,iVar16,*piVar1,0,0,*(uint *)(iVar20 + 4),local_2c,&local_30);
    *(undefined4 *)(iVar2 + iVar4) = 1;
    puVar3 = operator_new__(8);
    iVar2 = iVar2 + iVar4;
    iVar4 = iVar4 + 8;
    *(uint **)(iVar2 + 4) = puVar3;
    *puVar3 = local_2c[0];
    puVar3[1] = local_30;
  } while (iVar4 != 0x18);
  iVar4 = 0;
  iVar16 = 0;
  iVar20 = 0;
  do {
    iVar21 = DAT_00028570 + 0x283ec;
    *(undefined4 *)(iVar21 + iVar4) = 2;
    iVar21 = iVar21 + iVar4;
    puVar5 = operator_new__(0x10);
    puVar11 = *(undefined4 **)(DAT_00028574 + iVar4 + 0x28402);
    uVar9 = *puVar11;
    uVar12 = puVar11[1];
    *(undefined4 **)(iVar21 + 4) = puVar5;
    *puVar5 = uVar9;
    puVar5[1] = uVar12;
    iVar2 = GetStillSizeRow(this,iVar20 * 5 + iVar14);
    iVar8 = *piVar7;
    piVar17 = piVar7 + 2;
    piVar7 = piVar7 + 4;
    CalcStillData_S3(this,iVar8,*piVar17,*(int *)(DAT_00028578 + 0x28422 + iVar14 * 0x10),
                     *(int *)(DAT_00028578 + 0x28422 + iVar14 * 0x10 + 8),*(uint *)(iVar2 + 4),
                     local_2c,&local_30);
    iVar2 = *(int *)(iVar21 + 4);
    *(uint *)(iVar2 + 8) = local_2c[0];
    *(uint *)(iVar2 + 0xc) = local_30;
    __aeabi_idivmod(iVar16,3);
    if (extraout_r1_22 == 2) {
      iVar14 = iVar14 + 1;
    }
    __aeabi_idivmod(iVar16,0xf);
    if (extraout_r1_23 == 0xe) {
      iVar20 = iVar20 + 1;
      iVar14 = 0;
    }
    iVar16 = iVar16 + 1;
    iVar4 = iVar4 + 8;
  } while (iVar16 != 0x3c);
  iVar4 = 0;
  iVar16 = 0;
  iVar2 = 0;
  iVar20 = 0;
  do {
    iVar21 = DAT_0002857c + 0x2849a;
    *(undefined4 *)(iVar21 + iVar4) = 2;
    iVar21 = iVar21 + iVar4;
    puVar5 = operator_new__(0x10);
    puVar11 = *(undefined4 **)(DAT_00028580 + iVar4 + 0x284b0);
    uVar9 = *puVar11;
    uVar12 = puVar11[1];
    *(undefined4 **)(iVar21 + 4) = puVar5;
    *puVar5 = uVar9;
    puVar5[1] = uVar12;
    iVar14 = GetStillSizeRow(this,iVar20 * 5 + iVar2);
    iVar8 = *piVar10;
    piVar17 = piVar10 + 2;
    piVar10 = piVar10 + 4;
    CalcStillData_S3(this,iVar8,*piVar17,*(int *)(DAT_00028584 + 0x284d0 + iVar2 * 0x10),
                     *(int *)(DAT_00028584 + 0x284d0 + iVar2 * 0x10 + 8),*(uint *)(iVar14 + 4),
                     local_2c,&local_30);
    iVar14 = *(int *)(iVar21 + 4);
    *(uint *)(iVar14 + 8) = local_2c[0];
    *(uint *)(iVar14 + 0xc) = local_30;
    __aeabi_idivmod(iVar16,3);
    if (extraout_r1_24 == 2) {
      iVar2 = iVar2 + 1;
    }
    __aeabi_idivmod(iVar16,0xf);
    if (extraout_r1_25 == 0xe) {
      iVar20 = iVar20 + 1;
      iVar2 = 0;
    }
    iVar16 = iVar16 + 1;
    iVar4 = iVar4 + 8;
  } while (iVar16 != 0x3c);
  puVar3 = (uint *)(DAT_00028588 + 0x28536);
  if (((*puVar3 & 1) == 0) &&
     (iVar4 = __cxa_guard_acquire(puVar3), iVar20 = DAT_000287d8, iVar4 != 0)) {
    uVar9 = *(undefined4 *)(DAT_000287d4 + 0x285a6);
    uVar12 = *(undefined4 *)(DAT_000287d4 + 0x285aa);
    uVar13 = *(undefined4 *)(DAT_000287d4 + 0x285ae);
    puVar11 = (undefined4 *)(DAT_000287d4 + 0x285b2);
    *(undefined4 *)(DAT_000287d8 + 0x285a4) = *(undefined4 *)(DAT_000287d4 + 0x285a2);
    *(undefined4 *)(iVar20 + 0x285a8) = uVar9;
    *(undefined4 *)(iVar20 + 0x285ac) = uVar12;
    *(undefined4 *)(iVar20 + 0x285b0) = uVar13;
    iVar4 = DAT_000287dc;
    puVar5 = (undefined4 *)(DAT_000287dc + 0x285be);
    *(undefined4 *)(iVar20 + 0x285b4) = *puVar11;
    uVar9 = *(undefined4 *)(iVar4 + 0x285c2);
    uVar12 = *(undefined4 *)(iVar4 + 0x285c6);
    uVar13 = *(undefined4 *)(iVar4 + 0x285ca);
    *(undefined4 *)(iVar20 + 0x285b8) = *puVar5;
    *(undefined4 *)(iVar20 + 0x285bc) = uVar9;
    *(undefined4 *)(iVar20 + 0x285c0) = uVar12;
    *(undefined4 *)(iVar20 + 0x285c4) = uVar13;
    iVar16 = DAT_000287e0;
    puVar5 = (undefined4 *)(DAT_000287e0 + 0x285d2);
    *(undefined4 *)(iVar20 + 0x285c8) = *(undefined4 *)(iVar4 + 0x285ce);
    uVar9 = *(undefined4 *)(iVar16 + 0x285d6);
    uVar12 = *(undefined4 *)(iVar16 + 0x285da);
    uVar13 = *(undefined4 *)(iVar16 + 0x285de);
    *(undefined4 *)(iVar20 + 0x285cc) = *puVar5;
    *(undefined4 *)(iVar20 + 0x285d0) = uVar9;
    *(undefined4 *)(iVar20 + 0x285d4) = uVar12;
    *(undefined4 *)(iVar20 + 0x285d8) = uVar13;
    iVar4 = DAT_000287e4;
    puVar5 = (undefined4 *)(DAT_000287e4 + 0x285ec);
    *(undefined4 *)(iVar20 + 0x285dc) = *(undefined4 *)(iVar16 + 0x285e2);
    uVar9 = *(undefined4 *)(iVar4 + 0x285f0);
    uVar12 = *(undefined4 *)(iVar4 + 0x285f4);
    uVar13 = *(undefined4 *)(iVar4 + 0x285f8);
    *(undefined4 *)(iVar20 + 0x285e0) = *puVar5;
    *(undefined4 *)(iVar20 + 0x285e4) = uVar9;
    *(undefined4 *)(iVar20 + 0x285e8) = uVar12;
    *(undefined4 *)(iVar20 + 0x285ec) = uVar13;
    iVar16 = DAT_000287e8;
    puVar5 = (undefined4 *)(DAT_000287e8 + 0x28606);
    *(undefined4 *)(iVar20 + 0x285f0) = *(undefined4 *)(iVar4 + 0x285fc);
    uVar9 = *(undefined4 *)(iVar16 + 0x2860a);
    uVar12 = *(undefined4 *)(iVar16 + 0x2860e);
    uVar13 = *(undefined4 *)(iVar16 + 0x28612);
    *(undefined4 *)(iVar20 + 0x285f4) = *puVar5;
    *(undefined4 *)(iVar20 + 0x285f8) = uVar9;
    *(undefined4 *)(iVar20 + 0x285fc) = uVar12;
    *(undefined4 *)(iVar20 + 0x28600) = uVar13;
    iVar4 = DAT_000287ec;
    puVar5 = (undefined4 *)(DAT_000287ec + 0x28620);
    *(undefined4 *)(iVar20 + 0x28604) = *(undefined4 *)(iVar16 + 0x28616);
    uVar9 = *(undefined4 *)(iVar4 + 0x28624);
    uVar12 = *(undefined4 *)(iVar4 + 0x28628);
    uVar13 = *(undefined4 *)(iVar4 + 0x2862c);
    *(undefined4 *)(iVar20 + 0x28608) = *puVar5;
    *(undefined4 *)(iVar20 + 0x2860c) = uVar9;
    *(undefined4 *)(iVar20 + 0x28610) = uVar12;
    *(undefined4 *)(iVar20 + 0x28614) = uVar13;
    iVar16 = DAT_000287f0;
    puVar5 = (undefined4 *)(DAT_000287f0 + 0x2863a);
    *(undefined4 *)(iVar20 + 0x28618) = *(undefined4 *)(iVar4 + 0x28630);
    uVar9 = *(undefined4 *)(iVar16 + 0x2863e);
    uVar12 = *(undefined4 *)(iVar16 + 0x28642);
    uVar13 = *(undefined4 *)(iVar16 + 0x28646);
    *(undefined4 *)(iVar20 + 0x2861c) = *puVar5;
    *(undefined4 *)(iVar20 + 0x28620) = uVar9;
    *(undefined4 *)(iVar20 + 0x28624) = uVar12;
    *(undefined4 *)(iVar20 + 0x28628) = uVar13;
    iVar4 = DAT_000287f4;
    puVar5 = (undefined4 *)(DAT_000287f4 + 0x28654);
    *(undefined4 *)(iVar20 + 0x2862c) = *(undefined4 *)(iVar16 + 0x2864a);
    uVar9 = *(undefined4 *)(iVar4 + 0x28658);
    uVar12 = *(undefined4 *)(iVar4 + 0x2865c);
    uVar13 = *(undefined4 *)(iVar4 + 0x28660);
    *(undefined4 *)(iVar20 + 0x28630) = *puVar5;
    *(undefined4 *)(iVar20 + 0x28634) = uVar9;
    *(undefined4 *)(iVar20 + 0x28638) = uVar12;
    *(undefined4 *)(iVar20 + 0x2863c) = uVar13;
    iVar16 = DAT_000287f8;
    puVar5 = (undefined4 *)(DAT_000287f8 + 0x2866e);
    *(undefined4 *)(iVar20 + 0x28640) = *(undefined4 *)(iVar4 + 0x28664);
    uVar9 = *(undefined4 *)(iVar16 + 0x28672);
    uVar12 = *(undefined4 *)(iVar16 + 0x28676);
    uVar13 = *(undefined4 *)(iVar16 + 0x2867a);
    *(undefined4 *)(iVar20 + 0x28644) = *puVar5;
    *(undefined4 *)(iVar20 + 0x28648) = uVar9;
    *(undefined4 *)(iVar20 + 0x2864c) = uVar12;
    *(undefined4 *)(iVar20 + 0x28650) = uVar13;
    iVar4 = DAT_000287fc;
    puVar5 = (undefined4 *)(DAT_000287fc + 0x28688);
    *(undefined4 *)(iVar20 + 0x28654) = *(undefined4 *)(iVar16 + 0x2867e);
    uVar9 = *(undefined4 *)(iVar4 + 0x2868c);
    uVar12 = *(undefined4 *)(iVar4 + 0x28690);
    uVar13 = *(undefined4 *)(iVar4 + 0x28694);
    *(undefined4 *)(iVar20 + 0x28658) = *puVar5;
    *(undefined4 *)(iVar20 + 0x2865c) = uVar9;
    *(undefined4 *)(iVar20 + 0x28660) = uVar12;
    *(undefined4 *)(iVar20 + 0x28664) = uVar13;
    iVar16 = DAT_00028800;
    puVar5 = (undefined4 *)(DAT_00028800 + 0x286a2);
    *(undefined4 *)(iVar20 + 0x28668) = *(undefined4 *)(iVar4 + 0x28698);
    uVar9 = *(undefined4 *)(iVar16 + 0x286a6);
    uVar12 = *(undefined4 *)(iVar16 + 0x286aa);
    uVar13 = *(undefined4 *)(iVar16 + 0x286ae);
    *(undefined4 *)(iVar20 + 0x2866c) = *puVar5;
    *(undefined4 *)(iVar20 + 0x28670) = uVar9;
    *(undefined4 *)(iVar20 + 0x28674) = uVar12;
    *(undefined4 *)(iVar20 + 0x28678) = uVar13;
    iVar4 = DAT_00028804;
    puVar5 = (undefined4 *)(DAT_00028804 + 0x286bc);
    *(undefined4 *)(iVar20 + 0x2867c) = *(undefined4 *)(iVar16 + 0x286b2);
    uVar9 = *(undefined4 *)(iVar4 + 0x286c0);
    uVar12 = *(undefined4 *)(iVar4 + 0x286c4);
    uVar13 = *(undefined4 *)(iVar4 + 0x286c8);
    *(undefined4 *)(iVar20 + 0x28680) = *puVar5;
    *(undefined4 *)(iVar20 + 0x28684) = uVar9;
    *(undefined4 *)(iVar20 + 0x28688) = uVar12;
    *(undefined4 *)(iVar20 + 0x2868c) = uVar13;
    iVar16 = DAT_00028808;
    puVar5 = (undefined4 *)(DAT_00028808 + 0x286d6);
    *(undefined4 *)(iVar20 + 0x28690) = *(undefined4 *)(iVar4 + 0x286cc);
    uVar9 = *(undefined4 *)(iVar16 + 0x286da);
    uVar12 = *(undefined4 *)(iVar16 + 0x286de);
    uVar13 = *(undefined4 *)(iVar16 + 0x286e2);
    *(undefined4 *)(iVar20 + 0x28694) = *puVar5;
    *(undefined4 *)(iVar20 + 0x28698) = uVar9;
    *(undefined4 *)(iVar20 + 0x2869c) = uVar12;
    *(undefined4 *)(iVar20 + 0x286a0) = uVar13;
    iVar4 = DAT_0002880c;
    puVar5 = (undefined4 *)(DAT_0002880c + 0x286f0);
    *(undefined4 *)(iVar20 + 0x286a4) = *(undefined4 *)(iVar16 + 0x286e6);
    uVar9 = *(undefined4 *)(iVar4 + 0x286f4);
    uVar12 = *(undefined4 *)(iVar4 + 0x286f8);
    uVar13 = *(undefined4 *)(iVar4 + 0x286fc);
    *(undefined4 *)(iVar20 + 0x286a8) = *puVar5;
    *(undefined4 *)(iVar20 + 0x286ac) = uVar9;
    *(undefined4 *)(iVar20 + 0x286b0) = uVar12;
    *(undefined4 *)(iVar20 + 0x286b4) = uVar13;
    iVar16 = DAT_00028810;
    puVar5 = (undefined4 *)(DAT_00028810 + 0x2870a);
    *(undefined4 *)(iVar20 + 0x286b8) = *(undefined4 *)(iVar4 + 0x28700);
    uVar9 = *(undefined4 *)(iVar16 + 0x2870e);
    uVar12 = *(undefined4 *)(iVar16 + 0x28712);
    uVar13 = *(undefined4 *)(iVar16 + 0x28716);
    *(undefined4 *)(iVar20 + 0x286bc) = *puVar5;
    *(undefined4 *)(iVar20 + 0x286c0) = uVar9;
    *(undefined4 *)(iVar20 + 0x286c4) = uVar12;
    *(undefined4 *)(iVar20 + 0x286c8) = uVar13;
    iVar4 = DAT_00028814;
    puVar5 = (undefined4 *)(DAT_00028814 + 0x28724);
    *(undefined4 *)(iVar20 + 0x286cc) = *(undefined4 *)(iVar16 + 0x2871a);
    uVar9 = *(undefined4 *)(iVar4 + 0x28728);
    uVar12 = *(undefined4 *)(iVar4 + 0x2872c);
    uVar13 = *(undefined4 *)(iVar4 + 0x28730);
    *(undefined4 *)(iVar20 + 0x286d0) = *puVar5;
    *(undefined4 *)(iVar20 + 0x286d4) = uVar9;
    *(undefined4 *)(iVar20 + 0x286d8) = uVar12;
    *(undefined4 *)(iVar20 + 0x286dc) = uVar13;
    iVar16 = DAT_00028818;
    puVar5 = (undefined4 *)(DAT_00028818 + 0x2873e);
    *(undefined4 *)(iVar20 + 0x286e0) = *(undefined4 *)(iVar4 + 0x28734);
    uVar9 = *(undefined4 *)(iVar16 + 0x28742);
    uVar12 = *(undefined4 *)(iVar16 + 0x28746);
    uVar13 = *(undefined4 *)(iVar16 + 0x2874a);
    *(undefined4 *)(iVar20 + 0x286e4) = *puVar5;
    *(undefined4 *)(iVar20 + 0x286e8) = uVar9;
    *(undefined4 *)(iVar20 + 0x286ec) = uVar12;
    *(undefined4 *)(iVar20 + 0x286f0) = uVar13;
    iVar4 = DAT_0002881c;
    puVar5 = (undefined4 *)(DAT_0002881c + 0x28758);
    *(undefined4 *)(iVar20 + 0x286f4) = *(undefined4 *)(iVar16 + 0x2874e);
    uVar9 = *(undefined4 *)(iVar4 + 0x2875c);
    uVar12 = *(undefined4 *)(iVar4 + 0x28760);
    uVar13 = *(undefined4 *)(iVar4 + 0x28764);
    *(undefined4 *)(iVar20 + 0x286f8) = *puVar5;
    *(undefined4 *)(iVar20 + 0x286fc) = uVar9;
    *(undefined4 *)(iVar20 + 0x28700) = uVar12;
    *(undefined4 *)(iVar20 + 0x28704) = uVar13;
    iVar16 = DAT_00028820;
    puVar5 = (undefined4 *)(DAT_00028820 + 0x28772);
    *(undefined4 *)(iVar20 + 0x28708) = *(undefined4 *)(iVar4 + 0x28768);
    uVar9 = *(undefined4 *)(iVar16 + 0x28776);
    uVar12 = *(undefined4 *)(iVar16 + 0x2877a);
    uVar13 = *(undefined4 *)(iVar16 + 0x2877e);
    *(undefined4 *)(iVar20 + 0x2870c) = *puVar5;
    *(undefined4 *)(iVar20 + 0x28710) = uVar9;
    *(undefined4 *)(iVar20 + 0x28714) = uVar12;
    *(undefined4 *)(iVar20 + 0x28718) = uVar13;
    iVar4 = DAT_00028824;
    puVar5 = (undefined4 *)(DAT_00028824 + 0x2878c);
    *(undefined4 *)(iVar20 + 0x2871c) = *(undefined4 *)(iVar16 + 0x28782);
    uVar9 = *(undefined4 *)(iVar4 + 0x28790);
    uVar12 = *(undefined4 *)(iVar4 + 0x28794);
    uVar13 = *(undefined4 *)(iVar4 + 0x28798);
    *(undefined4 *)(iVar20 + 0x28720) = *puVar5;
    *(undefined4 *)(iVar20 + 0x28724) = uVar9;
    *(undefined4 *)(iVar20 + 0x28728) = uVar12;
    *(undefined4 *)(iVar20 + 0x2872c) = uVar13;
    *(undefined4 *)(iVar20 + 0x28730) = *(undefined4 *)(iVar4 + 0x2879c);
    uVar9 = *(undefined4 *)(DAT_00028828 + 0x287b2);
    uVar12 = *(undefined4 *)(DAT_00028828 + 0x287b6);
    uVar13 = *(undefined4 *)(DAT_00028828 + 0x287ba);
    puVar5 = (undefined4 *)(DAT_00028828 + 0x287be);
    *(undefined4 *)(iVar20 + 0x28734) = *(undefined4 *)(DAT_00028828 + 0x287ae);
    *(undefined4 *)(iVar20 + 0x28738) = uVar9;
    *(undefined4 *)(iVar20 + 0x2873c) = uVar12;
    *(undefined4 *)(iVar20 + 0x28740) = uVar13;
    *(undefined4 *)(iVar20 + 0x28744) = *puVar5;
    __cxa_guard_release(puVar3);
  }
  *(int *)(this + 8) = DAT_0002882c + 0x287c4;
  *(undefined4 *)(this + 0xc) = 0x15;
  return;
}


/* 00028830 */

/* MprCtrlStillMgr::PrintStillSize() */

void MprCtrlStillMgr::PrintStillSize(void)

{
  int in_r0;
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar1 = 0;
  MonCtrl::ConPrintfMessage(*(char **)(in_r0 + 0x10),DAT_0002888c + 0x28838);
  MonCtrl::ConPrintfMessage(*(char **)(in_r0 + 0x10),DAT_00028890 + 0x2884a);
  do {
    iVar2 = *(int *)(in_r0 + 4);
    MonCtrl::ConPrintfMessage(*(char **)(in_r0 + 0x10),DAT_00028894 + 0x28858,iVar1);
    iVar3 = iVar2 + iVar1 * 8;
    MonCtrl::ConPrintfMessage
              (*(char **)(in_r0 + 0x10),DAT_00028898 + 0x2886a,(uint)*(ushort *)(iVar2 + iVar1 * 8))
    ;
    iVar1 = iVar1 + 1;
    MonCtrl::ConPrintfMessage
              (*(char **)(in_r0 + 0x10),DAT_0002889c + 0x28876,(uint)*(ushort *)(iVar3 + 2));
    MonCtrl::ConPrintfMessage
              (*(char **)(in_r0 + 0x10),DAT_000288a0 + 0x28882,*(undefined4 *)(iVar3 + 4));
  } while (iVar1 != 99);
  return;
}


/* 000288a4 */

/* MprCtrlStillMgr::PrintStillData() */

void __thiscall MprCtrlStillMgr::PrintStillData(MprCtrlStillMgr *this)

{
  uint uVar1;
  
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x10),DAT_000294a0 + 0x288b8);
  uVar1 = 0;
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x10),DAT_000294a4 + 0x288c6);
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x10),DAT_000294a8 + 0x288d4);
  MonCtrl::ConPrintfMessage
            (*(char **)(this + 0x10),DAT_000294ac + 0x288e4,
             *(undefined4 *)(*(int *)(this + 8) + 0x10));
  while( true ) {
    if (*(uint *)(*(int *)(this + 8) + 0xc) <= uVar1) break;
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),4);
    uVar1 = uVar1 + 1;
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStrAndCRLF(*(char **)(this + 0x10));
  }
  uVar1 = 0;
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x10),DAT_000294c0 + 0x28958);
  MonCtrl::ConPrintfMessage
            (*(char **)(this + 0x10),DAT_000294c4 + 0x2896a,
             *(undefined4 *)(*(int *)(this + 8) + 0xec));
  while( true ) {
    if (*(uint *)(*(int *)(this + 8) + 0xe8) <= uVar1) break;
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),4);
    uVar1 = uVar1 + 1;
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStrAndCRLF(*(char **)(this + 0x10));
  }
  uVar1 = 0;
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x10),DAT_000294d8 + 0x289e4);
  MonCtrl::ConPrintfMessage
            (*(char **)(this + 0x10),DAT_000294dc + 0x289f6,
             *(undefined4 *)(*(int *)(this + 8) + 0x24));
  while( true ) {
    if (*(uint *)(*(int *)(this + 8) + 0x20) <= uVar1) break;
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),4);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    uVar1 = uVar1 + 1;
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStrAndCRLF(*(char **)(this + 0x10));
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStrAndCRLF(*(char **)(this + 0x10));
  }
  uVar1 = 0;
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x10),DAT_000294f4 + 0x28aac);
  MonCtrl::ConPrintfMessage
            (*(char **)(this + 0x10),DAT_000294f8 + 0x28ac0,
             *(undefined4 *)(*(int *)(this + 8) + 0x100));
  while( true ) {
    if (*(uint *)(*(int *)(this + 8) + 0xfc) <= uVar1) break;
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),4);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    uVar1 = uVar1 + 1;
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStrAndCRLF(*(char **)(this + 0x10));
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStrAndCRLF(*(char **)(this + 0x10));
  }
  uVar1 = 0;
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x10),DAT_00029510 + 0x28b78);
  MonCtrl::ConPrintfMessage
            (*(char **)(this + 0x10),DAT_00029514 + 0x28b88,
             *(undefined4 *)(*(int *)(this + 8) + 0x38));
  while( true ) {
    if (*(uint *)(*(int *)(this + 8) + 0x34) <= uVar1) break;
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),4);
    uVar1 = uVar1 + 1;
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStrAndCRLF(*(char **)(this + 0x10));
  }
  uVar1 = 0;
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x10),DAT_00029528 + 0x28bfc);
  MonCtrl::ConPrintfMessage
            (*(char **)(this + 0x10),DAT_0002952c + 0x28c0e,
             *(undefined4 *)(*(int *)(this + 8) + 0x114));
  while( true ) {
    if (*(uint *)(*(int *)(this + 8) + 0x110) <= uVar1) break;
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),4);
    uVar1 = uVar1 + 1;
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStrAndCRLF(*(char **)(this + 0x10));
  }
  uVar1 = 0;
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x10),DAT_00029540 + 0x28c86);
  MonCtrl::ConPrintfMessage
            (*(char **)(this + 0x10),DAT_00029544 + 0x28c96,
             *(undefined4 *)(*(int *)(this + 8) + 0x4c));
  while( true ) {
    if (*(uint *)(*(int *)(this + 8) + 0x48) <= uVar1) break;
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),4);
    uVar1 = uVar1 + 1;
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStrAndCRLF(*(char **)(this + 0x10));
  }
  uVar1 = 0;
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x10),DAT_00029558 + 0x28d0a);
  MonCtrl::ConPrintfMessage
            (*(char **)(this + 0x10),DAT_0002955c + 0x28d1c,
             *(undefined4 *)(*(int *)(this + 8) + 0x128));
  while( true ) {
    if (*(uint *)(*(int *)(this + 8) + 0x124) <= uVar1) break;
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),4);
    uVar1 = uVar1 + 1;
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStrAndCRLF(*(char **)(this + 0x10));
  }
  uVar1 = 0;
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x10),DAT_00029570 + 0x28d96);
  MonCtrl::ConPrintfMessage
            (*(char **)(this + 0x10),DAT_00029574 + 0x28da8,
             *(undefined4 *)(*(int *)(this + 8) + 0x60));
  while( true ) {
    if (*(uint *)(*(int *)(this + 8) + 0x5c) <= uVar1) break;
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),4);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    uVar1 = uVar1 + 1;
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStrAndCRLF(*(char **)(this + 0x10));
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStrAndCRLF(*(char **)(this + 0x10));
  }
  uVar1 = 0;
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x10),DAT_0002958c + 0x28e5e);
  MonCtrl::ConPrintfMessage
            (*(char **)(this + 0x10),DAT_00029590 + 0x28e72,
             *(undefined4 *)(*(int *)(this + 8) + 0x13c));
  while( true ) {
    if (*(uint *)(*(int *)(this + 8) + 0x138) <= uVar1) break;
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),4);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    uVar1 = uVar1 + 1;
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStrAndCRLF(*(char **)(this + 0x10));
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStrAndCRLF(*(char **)(this + 0x10));
  }
  uVar1 = 0;
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x10),DAT_000295a8 + 0x28f2c);
  MonCtrl::ConPrintfMessage
            (*(char **)(this + 0x10),DAT_000295ac + 0x28f3e,
             *(undefined4 *)(*(int *)(this + 8) + 0x74));
  while( true ) {
    if (*(uint *)(*(int *)(this + 8) + 0x70) <= uVar1) break;
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),4);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStrAndCRLF(*(char **)(this + 0x10));
    uVar1 = uVar1 + 1;
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStrAndCRLF(*(char **)(this + 0x10));
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStrAndCRLF(*(char **)(this + 0x10));
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStrAndCRLF(*(char **)(this + 0x10));
  }
  uVar1 = 0;
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x10),DAT_000295c4 + 0x29058);
  MonCtrl::ConPrintfMessage
            (*(char **)(this + 0x10),DAT_000295c8 + 0x2906e,
             *(undefined4 *)(*(int *)(this + 8) + 0x150));
  while( true ) {
    if (*(uint *)(*(int *)(this + 8) + 0x14c) <= uVar1) break;
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),4);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStrAndCRLF(*(char **)(this + 0x10));
    uVar1 = uVar1 + 1;
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStrAndCRLF(*(char **)(this + 0x10));
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStrAndCRLF(*(char **)(this + 0x10));
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStrAndCRLF(*(char **)(this + 0x10));
  }
  uVar1 = 0;
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x10),DAT_000295e0 + 0x29188);
  MonCtrl::ConPrintfMessage
            (*(char **)(this + 0x10),DAT_000295e4 + 0x2919a,
             *(undefined4 *)(*(int *)(this + 8) + 0x88));
  while( true ) {
    if (*(uint *)(*(int *)(this + 8) + 0x84) <= uVar1) break;
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),4);
    uVar1 = uVar1 + 1;
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStrAndCRLF(*(char **)(this + 0x10));
  }
  uVar1 = 0;
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x10),DAT_000295f8 + 0x29210);
  MonCtrl::ConPrintfMessage
            (*(char **)(this + 0x10),DAT_000295fc + 0x29220,
             *(undefined4 *)(*(int *)(this + 8) + 0x164));
  while( true ) {
    if (*(uint *)(*(int *)(this + 8) + 0x160) <= uVar1) break;
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),4);
    uVar1 = uVar1 + 1;
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStrAndCRLF(*(char **)(this + 0x10));
  }
  uVar1 = 0;
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x10),DAT_00029610 + 0x2928e);
  MonCtrl::ConPrintfMessage
            (*(char **)(this + 0x10),DAT_00029614 + 0x2929e,
             *(undefined4 *)(*(int *)(this + 8) + 0x9c));
  while( true ) {
    if (*(uint *)(*(int *)(this + 8) + 0x98) <= uVar1) break;
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),4);
    uVar1 = uVar1 + 1;
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStrAndCRLF(*(char **)(this + 0x10));
  }
  uVar1 = 0;
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x10),DAT_00029628 + 0x2930c);
  MonCtrl::ConPrintfMessage
            (*(char **)(this + 0x10),DAT_0002962c + 0x2931c,
             *(undefined4 *)(*(int *)(this + 8) + 0xb0));
  while( true ) {
    if (*(uint *)(*(int *)(this + 8) + 0xac) <= uVar1) break;
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),4);
    uVar1 = uVar1 + 1;
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStrAndCRLF(*(char **)(this + 0x10));
  }
  uVar1 = 0;
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x10),DAT_00029640 + 0x2938a);
  MonCtrl::ConPrintfMessage
            (*(char **)(this + 0x10),DAT_00029644 + 0x2939a,
             *(undefined4 *)(*(int *)(this + 8) + 0x178));
  while( true ) {
    if (*(uint *)(*(int *)(this + 8) + 0x174) <= uVar1) break;
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),4);
    uVar1 = uVar1 + 1;
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStrAndCRLF(*(char **)(this + 0x10));
  }
  uVar1 = 0;
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x10),DAT_00029658 + 0x29408);
  MonCtrl::ConPrintfMessage
            (*(char **)(this + 0x10),DAT_0002965c + 0x29418,
             *(undefined4 *)(*(int *)(this + 8) + 0xc4));
  while( true ) {
    if (*(uint *)(*(int *)(this + 8) + 0xc0) <= uVar1) break;
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),4);
    uVar1 = uVar1 + 1;
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStrAndCRLF(*(char **)(this + 0x10));
  }
  uVar1 = 0;
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x10),DAT_00029670 + 0x29486);
  MonCtrl::ConPrintfMessage
            (*(char **)(this + 0x10),DAT_00029674 + 0x29496,
             *(undefined4 *)(*(int *)(this + 8) + 0x18c));
  while( true ) {
    if (*(uint *)(*(int *)(this + 8) + 0x188) <= uVar1) break;
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),4);
    uVar1 = uVar1 + 1;
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStrAndCRLF(*(char **)(this + 0x10));
  }
  uVar1 = 0;
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x10),DAT_00029870 + 0x296e0);
  MonCtrl::ConPrintfMessage
            (*(char **)(this + 0x10),DAT_00029874 + 0x296f2,
             *(undefined4 *)(*(int *)(this + 8) + 0xd8));
  while( true ) {
    if (*(uint *)(*(int *)(this + 8) + 0xd4) <= uVar1) break;
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),4);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    uVar1 = uVar1 + 1;
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStrAndCRLF(*(char **)(this + 0x10));
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStrAndCRLF(*(char **)(this + 0x10));
  }
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x10),DAT_0002988c + 0x297a0);
  MonCtrl::ConPrintfMessage
            (*(char **)(this + 0x10),DAT_00029890 + 0x297b2,
             *(undefined4 *)(*(int *)(this + 8) + 0x1a0));
  for (uVar1 = 0; uVar1 < *(uint *)(*(int *)(this + 8) + 0x19c); uVar1 = uVar1 + 1) {
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),4);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStrAndCRLF(*(char **)(this + 0x10));
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10),8);
    MonCtrl::ConPutStrAndCRLF(*(char **)(this + 0x10));
  }
  return;
}


/* 000298a8 */

/* MprCtrlStillMgr::PrintStillBackup() */

void __thiscall MprCtrlStillMgr::PrintStillBackup(MprCtrlStillMgr *this)

{
  uint *puVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  undefined4 local_28;
  undefined4 local_24 [2];
  
  iVar5 = 0;
  local_24[0] = 0;
  local_28 = 0;
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x10),DAT_0002a438 + 0x298ba);
  iVar4 = DAT_0002a440;
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x10),DAT_0002a43c + 0x298ce);
  iVar4 = iVar4 + 0x298de;
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x10),DAT_0002a444 + 0x298e0);
  do {
    iVar6 = DAT_0002a448 + 0x298ee;
    iVar2 = BackupLib::GetEepData(*(uint *)(iVar6 + iVar5),'\x04',local_24);
    if (iVar2 < 0) {
      MonCtrl::ConPrintfMessage
                (*(char **)(this + 0x14),DAT_0002a44c + 0x29906,*(undefined4 *)(iVar6 + iVar5 + 4));
    }
    iVar2 = BackupLib::GetEepData(*(uint *)(iVar4 + 8),'\x04',&local_28);
    if (iVar2 < 0) {
      MonCtrl::ConPrintfMessage
                (*(char **)(this + 0x14),DAT_0002a450 + 0x29922,*(undefined4 *)(iVar4 + 0xc));
    }
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    iVar2 = DAT_0002a45c + iVar5;
    iVar5 = iVar5 + 0x10;
    MonCtrl::ConPutStr(*(char **)(this + 0x10),*(uint *)(iVar2 + 0x29948));
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10));
    MonCtrl::ConPutCRLF();
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    puVar1 = (uint *)(iVar4 + 0xc);
    iVar4 = iVar4 + 0x10;
    MonCtrl::ConPutStr(*(char **)(this + 0x10),*puVar1);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10));
    MonCtrl::ConPutCRLF();
    iVar2 = DAT_0002a464;
  } while (iVar5 != 0x3c0);
  iVar4 = 0;
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x10),DAT_0002a460 + 0x299a0);
  iVar2 = iVar2 + 0x299aa;
  do {
    iVar6 = DAT_0002a468 + 0x299b4;
    iVar5 = BackupLib::GetEepData(*(uint *)(iVar6 + iVar4),'\x04',local_24);
    if (iVar5 < 0) {
      MonCtrl::ConPrintfMessage
                (*(char **)(this + 0x14),DAT_0002a46c + 0x299cc,*(undefined4 *)(iVar6 + iVar4 + 4));
    }
    iVar5 = BackupLib::GetEepData(*(uint *)(iVar2 + 8),'\x04',&local_28);
    if (iVar5 < 0) {
      MonCtrl::ConPrintfMessage
                (*(char **)(this + 0x14),DAT_0002a470 + 0x299e8,*(undefined4 *)(iVar2 + 0xc));
    }
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    iVar5 = DAT_0002a47c + iVar4;
    iVar4 = iVar4 + 0x10;
    MonCtrl::ConPutStr(*(char **)(this + 0x10),*(uint *)(iVar5 + 0x29a0e));
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10));
    MonCtrl::ConPutCRLF();
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    puVar1 = (uint *)(iVar2 + 0xc);
    iVar2 = iVar2 + 0x10;
    MonCtrl::ConPutStr(*(char **)(this + 0x10),*puVar1);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10));
    MonCtrl::ConPutCRLF();
    iVar5 = DAT_0002a48c;
  } while (iVar4 != 0x3c0);
  iVar4 = 0;
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x10),DAT_0002a488 + 0x29a66);
  iVar5 = iVar5 + 0x29a70;
  do {
    iVar6 = DAT_0002a490 + 0x29a7a;
    iVar2 = BackupLib::GetEepData(*(uint *)(iVar6 + iVar4),'\x04',local_24);
    if (iVar2 < 0) {
      MonCtrl::ConPrintfMessage
                (*(char **)(this + 0x14),DAT_0002a494 + 0x29a92,*(undefined4 *)(iVar6 + iVar4 + 4));
    }
    iVar2 = BackupLib::GetEepData(*(uint *)(iVar5 + 8),'\x04',&local_28);
    if (iVar2 < 0) {
      MonCtrl::ConPrintfMessage
                (*(char **)(this + 0x14),DAT_0002a498 + 0x29aae,*(undefined4 *)(iVar5 + 0xc));
    }
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    iVar2 = DAT_0002a4a4 + iVar4;
    iVar4 = iVar4 + 0x10;
    MonCtrl::ConPutStr(*(char **)(this + 0x10),*(uint *)(iVar2 + 0x29ad4));
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10));
    MonCtrl::ConPutCRLF();
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    puVar1 = (uint *)(iVar5 + 0xc);
    iVar5 = iVar5 + 0x10;
    MonCtrl::ConPutStr(*(char **)(this + 0x10),*puVar1);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10));
    MonCtrl::ConPutCRLF();
    iVar2 = DAT_0002a4b0;
  } while (iVar4 != 0x180);
  iVar4 = 0;
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x10),DAT_0002a4ac + 0x29b2c);
  iVar2 = iVar2 + 0x29b36;
  do {
    iVar6 = DAT_0002a4b4 + 0x29b40;
    iVar5 = BackupLib::GetEepData(*(uint *)(iVar6 + iVar4),'\x04',local_24);
    if (iVar5 < 0) {
      MonCtrl::ConPrintfMessage
                (*(char **)(this + 0x14),DAT_0002a4bc + 0x29b58,*(undefined4 *)(iVar6 + iVar4 + 4));
    }
    iVar5 = BackupLib::GetEepData(*(uint *)(iVar2 + 8),'\x04',&local_28);
    if (iVar5 < 0) {
      MonCtrl::ConPrintfMessage
                (*(char **)(this + 0x14),DAT_0002a4c0 + 0x29b74,*(undefined4 *)(iVar2 + 0xc));
    }
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    iVar5 = DAT_0002a4cc + iVar4;
    iVar4 = iVar4 + 0x10;
    MonCtrl::ConPutStr(*(char **)(this + 0x10),*(uint *)(iVar5 + 0x29b9a));
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10));
    MonCtrl::ConPutCRLF();
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    puVar1 = (uint *)(iVar2 + 0xc);
    iVar2 = iVar2 + 0x10;
    MonCtrl::ConPutStr(*(char **)(this + 0x10),*puVar1);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10));
    MonCtrl::ConPutCRLF();
    iVar5 = DAT_0002a4d4;
  } while (iVar4 != 0x180);
  iVar4 = 0;
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x10),DAT_0002a4d0 + 0x29bf2);
  iVar5 = iVar5 + 0x29bfc;
  do {
    iVar6 = DAT_0002a4d8 + 0x29c06;
    iVar2 = BackupLib::GetEepData(*(uint *)(iVar6 + iVar4),'\x04',local_24);
    if (iVar2 < 0) {
      MonCtrl::ConPrintfMessage
                (*(char **)(this + 0x14),DAT_0002a4dc + 0x29c1e,*(undefined4 *)(iVar6 + iVar4 + 4));
    }
    iVar2 = BackupLib::GetEepData(*(uint *)(iVar5 + 8),'\x04',&local_28);
    if (iVar2 < 0) {
      MonCtrl::ConPrintfMessage
                (*(char **)(this + 0x14),DAT_0002a4e0 + 0x29c3a,*(undefined4 *)(iVar5 + 0xc));
    }
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    iVar2 = DAT_0002a4ec + iVar4;
    iVar4 = iVar4 + 0x10;
    MonCtrl::ConPutStr(*(char **)(this + 0x10),*(uint *)(iVar2 + 0x29c60));
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10));
    MonCtrl::ConPutCRLF();
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    puVar1 = (uint *)(iVar5 + 0xc);
    iVar5 = iVar5 + 0x10;
    MonCtrl::ConPutStr(*(char **)(this + 0x10),*puVar1);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10));
    MonCtrl::ConPutCRLF();
    iVar2 = DAT_0002a4f4;
  } while (iVar4 != 0x2d0);
  iVar4 = 0;
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x10),DAT_0002a4f0 + 0x29cb8);
  iVar2 = iVar2 + 0x29cc2;
  do {
    iVar6 = DAT_0002a4f8 + 0x29ccc;
    iVar5 = BackupLib::GetEepData(*(uint *)(iVar6 + iVar4),'\x04',local_24);
    if (iVar5 < 0) {
      MonCtrl::ConPrintfMessage
                (*(char **)(this + 0x14),DAT_0002a4fc + 0x29ce4,*(undefined4 *)(iVar6 + iVar4 + 4));
    }
    iVar5 = BackupLib::GetEepData(*(uint *)(iVar2 + 8),'\x04',&local_28);
    if (iVar5 < 0) {
      MonCtrl::ConPrintfMessage
                (*(char **)(this + 0x14),DAT_0002a500 + 0x29d00,*(undefined4 *)(iVar2 + 0xc));
    }
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    iVar5 = DAT_0002a50c + iVar4;
    iVar4 = iVar4 + 0x10;
    MonCtrl::ConPutStr(*(char **)(this + 0x10),*(uint *)(iVar5 + 0x29d26));
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10));
    MonCtrl::ConPutCRLF();
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    puVar1 = (uint *)(iVar2 + 0xc);
    iVar2 = iVar2 + 0x10;
    MonCtrl::ConPutStr(*(char **)(this + 0x10),*puVar1);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10));
    MonCtrl::ConPutCRLF();
    iVar5 = DAT_0002a514;
  } while (iVar4 != 0x2d0);
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x10),DAT_0002a510 + 0x29d7e);
  iVar5 = iVar5 + 0x29d88;
  iVar4 = 0;
  do {
    iVar2 = iVar4;
    iVar6 = DAT_0002a518 + 0x29d92;
    iVar4 = BackupLib::GetEepData(*(uint *)(iVar6 + iVar2),'\x04',local_24);
    if (iVar4 < 0) {
      MonCtrl::ConPrintfMessage
                (*(char **)(this + 0x14),DAT_0002a51c + 0x29daa,*(undefined4 *)(iVar6 + iVar2 + 4));
    }
    iVar4 = BackupLib::GetEepData(*(uint *)(iVar5 + 8),'\x04',&local_28);
    if (iVar4 < 0) {
      MonCtrl::ConPrintfMessage
                (*(char **)(this + 0x14),DAT_0002a520 + 0x29dc6,*(undefined4 *)(iVar5 + 0xc));
    }
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutStr(*(char **)(this + 0x10),*(uint *)(DAT_0002a52c + iVar2 + 0x29dec));
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10));
    MonCtrl::ConPutCRLF();
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    puVar1 = (uint *)(iVar5 + 0xc);
    iVar5 = iVar5 + 0x10;
    MonCtrl::ConPutStr(*(char **)(this + 0x10),*puVar1);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10));
    MonCtrl::ConPutCRLF();
    iVar6 = DAT_0002a534;
    iVar4 = iVar2 + 0x10;
  } while (iVar2 + 0x10 != 0x90);
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x10),DAT_0002a530 + 0x29e42);
  iVar6 = iVar6 + 0x29e4c;
  iVar4 = iVar2 + -0x80;
  do {
    iVar5 = iVar4;
    iVar2 = DAT_0002a538 + 0x29e56;
    iVar4 = BackupLib::GetEepData(*(uint *)(iVar2 + iVar5),'\x04',local_24);
    if (iVar4 < 0) {
      MonCtrl::ConPrintfMessage
                (*(char **)(this + 0x14),DAT_0002a53c + 0x29e6e,*(undefined4 *)(iVar2 + iVar5 + 4));
    }
    iVar4 = BackupLib::GetEepData(*(uint *)(iVar6 + 8),'\x04',&local_28);
    if (iVar4 < 0) {
      MonCtrl::ConPrintfMessage
                (*(char **)(this + 0x14),DAT_0002a540 + 0x29e8a,*(undefined4 *)(iVar6 + 0xc));
    }
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutStr(*(char **)(this + 0x10),*(uint *)(DAT_0002a54c + iVar5 + 0x29eb0));
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10));
    MonCtrl::ConPutCRLF();
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    puVar1 = (uint *)(iVar6 + 0xc);
    iVar6 = iVar6 + 0x10;
    MonCtrl::ConPutStr(*(char **)(this + 0x10),*puVar1);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10));
    MonCtrl::ConPutCRLF();
    iVar2 = DAT_0002a554;
    iVar4 = iVar5 + 0x10;
  } while (iVar5 + 0x10 != 0x30);
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x10),DAT_0002a550 + 0x29f06);
  iVar2 = iVar2 + 0x29f10;
  iVar4 = iVar5 + -0x20;
  do {
    iVar5 = iVar4;
    iVar6 = DAT_0002a558 + 0x29f1a;
    iVar4 = BackupLib::GetEepData(*(uint *)(iVar6 + iVar5),'\x04',local_24);
    if (iVar4 < 0) {
      MonCtrl::ConPrintfMessage
                (*(char **)(this + 0x14),DAT_0002a55c + 0x29f32,*(undefined4 *)(iVar6 + iVar5 + 4));
    }
    iVar4 = BackupLib::GetEepData(*(uint *)(iVar2 + 8),'\x04',&local_28);
    if (iVar4 < 0) {
      MonCtrl::ConPrintfMessage
                (*(char **)(this + 0x14),DAT_0002a560 + 0x29f4e,*(undefined4 *)(iVar2 + 0xc));
    }
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutStr(*(char **)(this + 0x10),*(uint *)(DAT_0002a56c + iVar5 + 0x29f74));
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10));
    MonCtrl::ConPutCRLF();
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    puVar1 = (uint *)(iVar2 + 0xc);
    iVar2 = iVar2 + 0x10;
    MonCtrl::ConPutStr(*(char **)(this + 0x10),*puVar1);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10));
    MonCtrl::ConPutCRLF();
    iVar6 = DAT_0002a574;
    iVar4 = iVar5 + 0x10;
  } while (iVar5 + 0x10 != 0x30);
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x10),DAT_0002a570 + 0x29fca);
  iVar6 = iVar6 + 0x29fd4;
  iVar4 = iVar5 + -0x20;
  do {
    iVar5 = iVar4;
    iVar2 = DAT_0002a578 + 0x29fde;
    iVar4 = BackupLib::GetEepData(*(uint *)(iVar2 + iVar5),'\x04',local_24);
    if (iVar4 < 0) {
      MonCtrl::ConPrintfMessage
                (*(char **)(this + 0x14),DAT_0002a57c + 0x29ff6,*(undefined4 *)(iVar2 + iVar5 + 4));
    }
    iVar4 = BackupLib::GetEepData(*(uint *)(iVar6 + 8),'\x04',&local_28);
    if (iVar4 < 0) {
      MonCtrl::ConPrintfMessage
                (*(char **)(this + 0x14),DAT_0002a580 + 0x2a012,*(undefined4 *)(iVar6 + 0xc));
    }
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutStr(*(char **)(this + 0x10),*(uint *)(DAT_0002a58c + iVar5 + 0x2a038));
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10));
    MonCtrl::ConPutCRLF();
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    puVar1 = (uint *)(iVar6 + 0xc);
    iVar6 = iVar6 + 0x10;
    MonCtrl::ConPutStr(*(char **)(this + 0x10),*puVar1);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10));
    MonCtrl::ConPutCRLF();
    iVar2 = DAT_0002a594;
    iVar4 = iVar5 + 0x10;
  } while (iVar5 + 0x10 != 0x30);
  iVar5 = iVar5 + -0x20;
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x10),DAT_0002a590 + 0x2a08e);
  iVar2 = iVar2 + 0x2a098;
  do {
    iVar6 = DAT_0002a598 + 0x2a0a2;
    iVar4 = BackupLib::GetEepData(*(uint *)(iVar6 + iVar5),'\x04',local_24);
    if (iVar4 < 0) {
      MonCtrl::ConPrintfMessage
                (*(char **)(this + 0x14),DAT_0002a59c + 0x2a0ba,*(undefined4 *)(iVar6 + iVar5 + 4));
    }
    iVar4 = BackupLib::GetEepData(*(uint *)(iVar2 + 8),'\x04',&local_28);
    if (iVar4 < 0) {
      MonCtrl::ConPrintfMessage
                (*(char **)(this + 0x14),DAT_0002a5a0 + 0x2a0d6,*(undefined4 *)(iVar2 + 0xc));
    }
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    iVar4 = DAT_0002a5ac + iVar5;
    iVar5 = iVar5 + 0x10;
    MonCtrl::ConPutStr(*(char **)(this + 0x10),*(uint *)(iVar4 + 0x2a0fc));
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10));
    MonCtrl::ConPutCRLF();
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    puVar1 = (uint *)(iVar2 + 0xc);
    iVar2 = iVar2 + 0x10;
    MonCtrl::ConPutStr(*(char **)(this + 0x10),*puVar1);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10));
    MonCtrl::ConPutCRLF();
  } while (iVar5 != 0x30);
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x10),DAT_0002a5b0 + 0x2a150);
  iVar4 = BackupLib::GetEepData(DAT_0002a434,'\x04',local_24);
  if (iVar4 < 0) {
    MonCtrl::ConPrintfMessage(*(char **)(this + 0x14),DAT_0002a5b4 + 0x2a16a);
  }
  iVar4 = DAT_0002a5bc;
  MonCtrl::ConPutStr(*(char **)(this + 0x10));
  iVar4 = iVar4 + 0x2a18c;
  MonCtrl::ConPutStr(*(char **)(this + 0x10),DAT_0002a5c0 + 0x2a18a);
  MonCtrl::ConPutStr(*(char **)(this + 0x10));
  MonCtrl::ConPutDec(*(uint *)(this + 0x10));
  MonCtrl::ConPutCRLF();
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x10),DAT_0002a5c8 + 0x2a1b2);
  iVar5 = 0;
  do {
    iVar2 = iVar5;
    iVar6 = DAT_0002a5cc + 0x2a1c0;
    iVar5 = BackupLib::GetEepData(*(uint *)(iVar6 + iVar2),'\x04',local_24);
    if (iVar5 < 0) {
      MonCtrl::ConPrintfMessage
                (*(char **)(this + 0x14),DAT_0002a5d0 + 0x2a1d8,*(undefined4 *)(iVar6 + iVar2 + 4));
    }
    iVar5 = BackupLib::GetEepData(*(uint *)(iVar4 + 8),'\x04',&local_28);
    if (iVar5 < 0) {
      MonCtrl::ConPrintfMessage
                (*(char **)(this + 0x14),DAT_0002a5d4 + 0x2a1f2,*(undefined4 *)(iVar4 + 0xc));
    }
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutStr(*(char **)(this + 0x10),*(uint *)(DAT_0002a5e0 + iVar2 + 0x2a216));
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10));
    MonCtrl::ConPutCRLF();
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    puVar1 = (uint *)(iVar4 + 0xc);
    iVar4 = iVar4 + 0x10;
    MonCtrl::ConPutStr(*(char **)(this + 0x10),*puVar1);
    MonCtrl::ConPutStr(*(char **)(this + 0x10));
    MonCtrl::ConPutDec(*(uint *)(this + 0x10));
    MonCtrl::ConPutCRLF();
    iVar6 = DAT_0002a5e8;
    iVar5 = iVar2 + 0x10;
  } while (iVar2 + 0x10 != 0x50);
  iVar2 = iVar2 + -0x40;
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x10),DAT_0002a5e4 + 0x2a26a);
  iVar6 = iVar6 + 0x2a272;
  do {
    iVar4 = DAT_0002a5ec + 0x2a278;
    uVar3 = *(uint *)(iVar4 + iVar2);
    if ((uVar3 != 0) && (uVar7 = *(uint *)(iVar6 + 8), uVar7 != 0)) {
      iVar5 = BackupLib::GetEepData(uVar3,'\x04',local_24);
      if (iVar5 < 0) {
        MonCtrl::ConPrintfMessage
                  (*(char **)(this + 0x14),DAT_0002a5f0 + 0x2a2a0,*(undefined4 *)(iVar4 + iVar2 + 4)
                  );
      }
      iVar4 = BackupLib::GetEepData(uVar7,'\x04',&local_28);
      if (iVar4 < 0) {
        MonCtrl::ConPrintfMessage
                  (*(char **)(this + 0x14),DAT_0002a5f4 + 0x2a2ba,*(undefined4 *)(iVar6 + 0xc));
      }
      MonCtrl::ConPutStr(*(char **)(this + 0x10));
      MonCtrl::ConPutStr(*(char **)(this + 0x10),*(uint *)(DAT_0002a600 + iVar2 + 0x2a2de));
      MonCtrl::ConPutStr(*(char **)(this + 0x10));
      MonCtrl::ConPutDec(*(uint *)(this + 0x10));
      MonCtrl::ConPutCRLF();
      MonCtrl::ConPutStr(*(char **)(this + 0x10));
      MonCtrl::ConPutStr(*(char **)(this + 0x10),*(uint *)(iVar6 + 0xc));
      MonCtrl::ConPutStr(*(char **)(this + 0x10));
      MonCtrl::ConPutDec(*(uint *)(this + 0x10));
      MonCtrl::ConPutCRLF();
    }
    iVar2 = iVar2 + 0x10;
    iVar6 = iVar6 + 0x10;
  } while (iVar2 != 0x60);
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x10),DAT_0002a604 + 0x2a330);
  iVar4 = BackupLib::GetEepData(DAT_0002a480,'\x04',local_24);
  if (iVar4 < 0) {
    MonCtrl::ConPrintfMessage(*(char **)(this + 0x14),DAT_0002a608 + 0x2a34a,DAT_0002a60c + 0x2a34c)
    ;
  }
  iVar4 = BackupLib::GetEepData(DAT_0002a484,'\x04',&local_28);
  if (iVar4 < 0) {
    MonCtrl::ConPrintfMessage(*(char **)(this + 0x14),DAT_0002a610 + 0x2a366,DAT_0002a614 + 0x2a368)
    ;
  }
  MonCtrl::ConPutStr(*(char **)(this + 0x10));
  MonCtrl::ConPutStr(*(char **)(this + 0x10),DAT_0002a620 + 0x2a382);
  MonCtrl::ConPutStr(*(char **)(this + 0x10));
  MonCtrl::ConPutDec(*(uint *)(this + 0x10));
  MonCtrl::ConPutCRLF();
  MonCtrl::ConPutStr(*(char **)(this + 0x10));
  MonCtrl::ConPutStr(*(char **)(this + 0x10),DAT_0002a624 + 0x2a3ae);
  MonCtrl::ConPutStr(*(char **)(this + 0x10));
  MonCtrl::ConPutDec(*(uint *)(this + 0x10));
  MonCtrl::ConPutCRLF();
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x10),DAT_0002a628 + 0x2a3ce);
  iVar4 = BackupLib::GetEepData(DAT_0002a4a8,'\x04',local_24);
  if (iVar4 < 0) {
    MonCtrl::ConPrintfMessage(*(char **)(this + 0x14),DAT_0002a62c + 0x2a3e6);
  }
  MonCtrl::ConPutStr(*(char **)(this + 0x10));
  MonCtrl::ConPutStr(*(char **)(this + 0x10),DAT_0002a634 + 0x2a400);
  MonCtrl::ConPutStr(*(char **)(this + 0x10));
  MonCtrl::ConPutDec(*(uint *)(this + 0x10));
  MonCtrl::ConPutCRLF();
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x10),DAT_0002a63c + 0x2a424);
  iVar4 = BackupLib::GetEepData(DAT_0002a4b8,'\x04',local_24);
  if (iVar4 < 0) {
    MonCtrl::ConPrintfMessage(*(char **)(this + 0x14),DAT_0002a8f0 + 0x2a64a);
  }
  MonCtrl::ConPutStr(*(char **)(this + 0x10));
  MonCtrl::ConPutStr(*(char **)(this + 0x10),DAT_0002a8f8 + 0x2a664);
  MonCtrl::ConPutStr(*(char **)(this + 0x10));
  MonCtrl::ConPutDec(*(uint *)(this + 0x10));
  MonCtrl::ConPutCRLF();
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x10),DAT_0002a900 + 0x2a688);
  iVar4 = BackupLib::GetEepData(DAT_0002a8d4,'\x04',local_24);
  if (iVar4 < 0) {
    MonCtrl::ConPrintfMessage(*(char **)(this + 0x14),DAT_0002a904 + 0x2a6a0);
  }
  MonCtrl::ConPutStr(*(char **)(this + 0x10));
  MonCtrl::ConPutStr(*(char **)(this + 0x10),DAT_0002a90c + 0x2a6ba);
  MonCtrl::ConPutStr(*(char **)(this + 0x10));
  MonCtrl::ConPutDec(*(uint *)(this + 0x10));
  MonCtrl::ConPutCRLF();
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x10),DAT_0002a914 + 0x2a6de);
  iVar4 = BackupLib::GetEepData(DAT_0002a8d8,'\x04',local_24);
  if (iVar4 < 0) {
    MonCtrl::ConPrintfMessage(*(char **)(this + 0x14),DAT_0002a918 + 0x2a6f6);
  }
  MonCtrl::ConPutStr(*(char **)(this + 0x10));
  MonCtrl::ConPutStr(*(char **)(this + 0x10),DAT_0002a920 + 0x2a710);
  MonCtrl::ConPutStr(*(char **)(this + 0x10));
  MonCtrl::ConPutDec(*(uint *)(this + 0x10));
  MonCtrl::ConPutCRLF();
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x10),DAT_0002a928 + 0x2a734);
  iVar4 = BackupLib::GetEepData(DAT_0002a8dc,'\x04',local_24);
  if (iVar4 < 0) {
    MonCtrl::ConPrintfMessage(*(char **)(this + 0x14),DAT_0002a92c + 0x2a74c);
  }
  MonCtrl::ConPutStr(*(char **)(this + 0x10));
  MonCtrl::ConPutStr(*(char **)(this + 0x10),DAT_0002a934 + 0x2a766);
  MonCtrl::ConPutStr(*(char **)(this + 0x10));
  MonCtrl::ConPutDec(*(uint *)(this + 0x10));
  MonCtrl::ConPutCRLF();
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x10),DAT_0002a93c + 0x2a78a);
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x10),DAT_0002a940 + 0x2a794);
  MonCtrl::ConPrintfMessage(*(char **)(this + 0x10),DAT_0002a944 + 0x2a79e);
  iVar4 = BackupLib::GetEepData(DAT_0002a8e0,'\x04',local_24);
  if (iVar4 < 0) {
    MonCtrl::ConPrintfMessage(*(char **)(this + 0x14),DAT_0002a948 + 0x2a7b6);
  }
  MonCtrl::ConPutStr(*(char **)(this + 0x10));
  MonCtrl::ConPutStr(*(char **)(this + 0x10),DAT_0002a950 + 0x2a7d0);
  MonCtrl::ConPutStr(*(char **)(this + 0x10));
  MonCtrl::ConPutDec(*(uint *)(this + 0x10));
  MonCtrl::ConPutCRLF();
  iVar4 = BackupLib::GetEepData(DAT_0002a8e4,'\x04',local_24);
  if (iVar4 < 0) {
    MonCtrl::ConPrintfMessage(*(char **)(this + 0x14),DAT_0002a958 + 0x2a802);
  }
  MonCtrl::ConPutStr(*(char **)(this + 0x10));
  MonCtrl::ConPutStr(*(char **)(this + 0x10),DAT_0002a960 + 0x2a81c);
  MonCtrl::ConPutStr(*(char **)(this + 0x10));
  MonCtrl::ConPutDec(*(uint *)(this + 0x10));
  MonCtrl::ConPutCRLF();
  iVar4 = BackupLib::GetEepData(DAT_0002a8e8,'\x04',local_24);
  if (iVar4 < 0) {
    MonCtrl::ConPrintfMessage(*(char **)(this + 0x14),DAT_0002a968 + 0x2a84e);
  }
  MonCtrl::ConPutStr(*(char **)(this + 0x10));
  MonCtrl::ConPutStr(*(char **)(this + 0x10),DAT_0002a970 + 0x2a868);
  MonCtrl::ConPutStr(*(char **)(this + 0x10));
  MonCtrl::ConPutDec(*(uint *)(this + 0x10));
  MonCtrl::ConPutCRLF();
  iVar4 = BackupLib::GetEepData(DAT_0002a8ec,'\x04',local_24);
  if (iVar4 < 0) {
    MonCtrl::ConPrintfMessage(*(char **)(this + 0x14),DAT_0002a978 + 0x2a89a);
  }
  MonCtrl::ConPutStr(*(char **)(this + 0x10));
  MonCtrl::ConPutStr(*(char **)(this + 0x10),DAT_0002a980 + 0x2a8b0);
  MonCtrl::ConPutStr(*(char **)(this + 0x10));
  MonCtrl::ConPutDec(*(uint *)(this + 0x10));
  MonCtrl::ConPutCRLF();
  return;
}


/* 0002a988 */

/* BackupLib::GetEepData(unsigned int, unsigned char, void*) */

ulonglong BackupLib::GetEepData(uint param_1,uchar param_2,void *param_3)

{
  ulonglong uVar1;
  
  if (param_3 == (void *)0x0) {
    return (ulonglong)CONCAT14(param_2,0xffffff9c);
  }
  uVar1 = (*(code *)PTR_Backup_read_0004bd5c)(param_1,param_3);
  return uVar1;
}


/* 0002a99e */

/* BackupLib::SetEepData(unsigned int, unsigned char, void*) */

undefined4 BackupLib::SetEepData(uint param_1,uchar param_2,void *param_3)

{
  undefined4 uVar1;
  
  if (param_3 == (void *)0x0) {
    return 0xffffff9c;
  }
  uVar1 = (*(code *)PTR_Backup_write_0004bfc4)(199,param_1);
  return uVar1;
}


/* 0002a9b6 */

/* BackupLib::GetDataSize(unsigned int) */

void BackupLib::GetDataSize(uint param_1)

{
  (*(code *)PTR_Backup_get_datasize_0004c1f8)(param_1);
  return;
}


/* 0002a9c2 */

void FUN_0002a9c2(int param_1,undefined4 param_2)

{
  *(undefined4 *)(param_1 + -4) = param_2;
  return;
}


/* 0002a9cc */

/* DmmAccess::Init(bool) */

void DmmAccess::Init(bool param_1)

{
  ObjLock *this;
  undefined4 uVar1;
  int iVar2;
  char *pcVar3;
  int iVar4;
  byte *pbVar5;
  undefined4 *puVar6;
  
  iVar4 = DAT_0002aa60 + 0x2a9dc;
  pcVar3 = *(char **)(iVar4 + DAT_0002aa64);
  if (*pcVar3 != '\0') {
    this = operator_new(0x1c);
    MWF::ObjLock::ObjLock(this);
    **(undefined4 **)(iVar4 + DAT_0002aa68) = this;
    *pcVar3 = '\0';
  }
  memset(*(void **)(iVar4 + DAT_0002aa6c),0,0x68);
  pcVar3 = (char *)MprCtrlMcmd::GetMonMsg();
  puVar6 = *(undefined4 **)(iVar4 + DAT_0002aa70);
  *puVar6 = pcVar3;
  MonCtrl::ConPutMessage(pcVar3);
  uVar1 = MprCtrlMcmd::GetMonErr();
  **(undefined4 **)(iVar4 + DAT_0002aa78) = uVar1;
  uVar1 = MprCtrlMcmd::GetMonDbg();
  iVar2 = DAT_0002aa80 + 0x2aa34;
  **(undefined4 **)(iVar4 + DAT_0002aa7c) = uVar1;
  pcVar3 = (char *)*puVar6;
  pbVar5 = *(byte **)(iVar4 + DAT_0002aa84);
  *pbVar5 = param_1;
  MonCtrl::ConPrintfMessage(pcVar3,iVar2,(uint)param_1);
  MprCtrlLog::SetParamLog('r',0,0,(ushort)*pbVar5,0x62);
  return;
}


/* 0002aa88 */

/* DmmAccess::DmmAccess(bool) */

DmmAccess * __thiscall DmmAccess::DmmAccess(DmmAccess *this,bool param_1)

{
  int *piVar1;
  
  piVar1 = *(int **)(DAT_0002aaac + 0x2aa90 + DAT_0002aab0);
  if (*piVar1 == 0) {
    Init(param_1);
    *piVar1 = *piVar1 + 1;
  }
  return this;
}


/* 0002aab4 */

/* DmmAccess::Quit() */

void DmmAccess::Quit(void)

{
  int *piVar1;
  int iVar2;
  int *piVar3;
  
  iVar2 = DAT_0002aad8 + 0x2aac0;
  piVar3 = *(int **)(iVar2 + DAT_0002aadc);
  piVar1 = (int *)*piVar3;
  if (piVar1 != (int *)0x0) {
    (**(code **)(*piVar1 + 4))();
    *piVar3 = 0;
  }
  **(undefined1 **)(iVar2 + DAT_0002aae0) = 1;
  return;
}


/* 0002aae4 */

/* DmmAccess::~DmmAccess() */

DmmAccess * __thiscall DmmAccess::~DmmAccess(DmmAccess *this)

{
  int *piVar1;
  
  piVar1 = *(int **)(DAT_0002ab04 + 0x2aaec + DAT_0002ab08);
  if (*piVar1 != 0) {
    Quit();
    *piVar1 = *piVar1 + -1;
  }
  return this;
}


/* 0002ab0c */

/* DmmAccess::BufFree(unsigned char*) */

void DmmAccess::BufFree(uchar *param_1)

{
  if (param_1 == (uchar *)0x0) {
    return;
  }
  MonCtrl::ConPrintfMessage
            ((char *)**(undefined4 **)(DAT_0002ab34 + 0x2ab14 + DAT_0002ab38),DAT_0002ab3c + 0x2ab22
             ,param_1);
  (*(code *)PTR_free_0004be9c)(param_1);
  return;
}


/* 0002ab40 */

/* DmmAccess::UnitTypeTableSelect(int) */

int DmmAccess::UnitTypeTableSelect(int param_1)

{
  switch(param_1) {
  case 0:
    return DAT_0002abf4 + 0x2ab6c;
  case 1:
    return (int)&DAT_0002abf4 + DAT_0002ac4c;
  case 2:
    return DAT_0002abf8 + 0x2ab72;
  case 3:
  case 4:
    return DAT_0002abfc + 0x2ab78;
  default:
    return 0;
  case 6:
    return DAT_0002ac00 + 0x2ab7e;
  case 7:
    return DAT_0002ac04 + 0x2ab84;
  case 9:
    return DAT_0002ac08 + 0x2ab8a;
  case 10:
    return DAT_0002ac0c + 0x2ab90;
  case 0xb:
    return DAT_0002ac10 + 0x2ab96;
  case 0xc:
    return DAT_0002ac14 + 0x2ab9c;
  case 0xd:
    return DAT_0002ac18 + 0x2aba2;
  case 0xe:
    return DAT_0002ac1c + 0x2aba8;
  case 0xf:
    return DAT_0002ac20 + 0x2abae;
  case 0x10:
    return DAT_0002ac24 + 0x2abb4;
  case 0x11:
    return DAT_0002ac28 + 0x2abba;
  case 0x12:
    return DAT_0002ac2c + 0x2abc0;
  case 0x13:
    return DAT_0002ac30 + 0x2abc6;
  case 0x14:
    return DAT_0002ac34 + 0x2abcc;
  case 0x15:
    return DAT_0002ac38 + 0x2abd2;
  case 0x16:
    return DAT_0002ac3c + 0x2abd8;
  case 0x17:
    return DAT_0002ac40 + 0x2abde;
  case 0x18:
    return DAT_0002ac44 + 0x2abe4;
  case 0x19:
    return DAT_0002ac48 + 0x2abea;
  }
}


/* 0002ac50 */

/* DmmAccess::GetUnitHandle(void*) */

void DmmAccess::GetUnitHandle(void *param_1)

{
  (*(code *)PTR_GetUnitHandle_0004be64)(param_1);
  return;
}


/* 0002ac5c */

/* DmmAccess::GetExtListCount(void*) */

void DmmAccess::GetExtListCount(void *param_1)

{
                    /* WARNING: Could not recover jumptable at 0x0001fbfc. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*(code *)PTR_GetExtListCount_0004c238)(param_1);
  return;
}


/* 0002ac68 */

/* DmmAccess::GetExtListTop(void*) */

void DmmAccess::GetExtListTop(void *param_1)

{
                    /* WARNING: Could not recover jumptable at 0x0001f684. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*(code *)PTR_GetExtListTop_0004c078)(param_1);
  return;
}


/* 0002ac74 */

/* DmmAccess::GetDMMRetMsg(short) */

int DmmAccess::GetDMMRetMsg(short param_1)

{
  switch(param_1) {
  case 0:
    return DAT_0002acd8 + 0x2ac96;
  case 1:
    return DAT_0002acf0 + 0x2acba;
  case 2:
    return DAT_0002acf4 + 0x2acc0;
  case 3:
    return DAT_0002acf8 + 0x2acc6;
  default:
    return DAT_0002ad00 + 0x2acd2;
  case 6:
    return DAT_0002acfc + 0x2accc;
  case -6:
    return DAT_0002acec + 0x2acb4;
  case -5:
    return DAT_0002ace8 + 0x2acae;
  case -4:
    return DAT_0002ace4 + 0x2aca8;
  case -3:
    return DAT_0002ace0 + 0x2aca2;
  case -2:
    return DAT_0002acdc + 0x2ac9c;
  case -1:
    return (int)&DAT_0002acd8 + DAT_0002ad04;
  }
}


/* 0002ad08 */

/* DmmAccess::CheckDMMRetCode(short, char*) */

int DmmAccess::CheckDMMRetCode(short param_1,char *param_2)

{
  int iVar1;
  
  iVar1 = 1 - param_1;
  if (1 < (uint)(int)param_1) {
    iVar1 = 0;
  }
  if (param_2 != (char *)0x0) {
    GetDMMRetMsg(param_1);
  }
  return iVar1;
}


/* 0002ad20 */

/* DmmAccess::GetOSALRetMsg(OSAL_ERR) */

undefined * DmmAccess::GetOSALRetMsg(int param_1)

{
  if (param_1 == DAT_0002ad70) {
    return (undefined *)(DAT_0002ad7c + 0x2ad56);
  }
  if (param_1 < DAT_0002ad70) {
    if (param_1 == -0x400) {
      return &UNK_0002ad6e + DAT_0002ad8c;
    }
    if (param_1 == DAT_0002ad70 + -1) {
      return (undefined *)(DAT_0002ad78 + 0x2ad50);
    }
  }
  else {
    if (param_1 == -0x3fc) {
      return (undefined *)(DAT_0002ad84 + 0x2ad62);
    }
    if (param_1 < -0x3fc) {
      return (undefined *)(DAT_0002ad80 + 0x2ad5c);
    }
    if (param_1 == 0) {
      return (undefined *)(DAT_0002ad74 + 0x2ad4a);
    }
  }
  return (undefined *)(DAT_0002ad88 + 0x2ad68);
}


/* 0002ad90 */

/* DmmAccess::CheckOSALRetCode(OSAL_ERR, char*) */

int DmmAccess::CheckOSALRetCode(uint param_1,int param_2)

{
  int iVar1;
  
  iVar1 = 1 - param_1;
  if (1 < param_1) {
    iVar1 = 0;
  }
  if (param_2 != 0) {
    GetOSALRetMsg();
  }
  return iVar1;
}


/* 0002ada8 */

/* DmmAccess::DmmCloseORFree_body(unsigned short, unsigned short, unsigned short) */

int DmmAccess::DmmCloseORFree_body(ushort param_1,ushort param_2,ushort param_3)

{
  ushort uVar1;
  ushort *puVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  int iVar6;
  undefined4 *puVar7;
  char *pcVar8;
  uint uVar9;
  undefined4 local_30;
  ushort *local_2c [2];
  
  local_30 = 0;
  local_2c[0] = (ushort *)0x0;
  iVar3 = osal_dynamic_id(0x2a,199,&local_30);
  iVar6 = DAT_0002af88 + 0x2add6;
  if (iVar3 != 0) {
    return 0;
  }
  uVar4 = osal_valloc_msg_wait(DAT_0002af84,local_2c,0x18,0);
  iVar3 = CheckOSALRetCode(uVar4,0);
  puVar2 = local_2c[0];
  if (iVar3 == 0) {
    puVar7 = *(undefined4 **)(iVar6 + DAT_0002af8c);
    MonCtrl::ConPrintfMessage((char *)*puVar7,DAT_0002af90 + 0x2adfe);
    pcVar8 = (char *)*puVar7;
    uVar4 = GetOSALRetMsg(uVar4);
    MonCtrl::ConPrintfMessage(pcVar8,DAT_0002af94 + 0x2ae10,uVar4);
    iVar3 = 0;
  }
  else {
    memset(local_2c[0],0,0x18);
    *puVar2 = param_2;
    puVar2[1] = param_1;
    FUN_0002a9c2(local_2c[0],local_30);
    iVar3 = DAT_0002af98;
    puVar2[10] = 0;
    puVar2[0xb] = param_3;
    puVar7 = *(undefined4 **)(iVar6 + iVar3);
    MonCtrl::ConPrintfMessage((char *)*puVar7,DAT_0002af9c + 0x2ae52,(uint)param_1,0);
    uVar4 = osal_snd_msg(DAT_0002af84,local_2c[0]);
    iVar3 = CheckOSALRetCode(uVar4,0);
    if (iVar3 == 0) {
      puVar7 = *(undefined4 **)(iVar6 + DAT_0002af8c);
      MonCtrl::ConPrintfMessage((char *)*puVar7,DAT_0002afa0 + 0x2ae74,uVar4);
      pcVar8 = (char *)*puVar7;
      uVar4 = GetOSALRetMsg(uVar4);
      iVar6 = DAT_0002afa4 + 0x2ae86;
    }
    else {
      uVar4 = osal_rcv_msg_tmo(local_30,local_2c,0xffffffff);
      iVar3 = CheckOSALRetCode(uVar4,0);
      puVar2 = local_2c[0];
      if (iVar3 != 0) {
        uVar1 = local_2c[0][1];
        iVar3 = CheckDMMRetCode(uVar1,(char *)0x0);
        if (iVar3 == 0) {
          puVar7 = *(undefined4 **)(iVar6 + DAT_0002af8c);
          MonCtrl::ConPrintfMessage((char *)*puVar7,DAT_0002afb0 + 0x2aeea,(int)(short)uVar1);
          pcVar8 = (char *)*puVar7;
          uVar4 = GetDMMRetMsg(uVar1);
          MonCtrl::ConPrintfMessage(pcVar8,DAT_0002afb4 + 0x2aefc,uVar4);
          MprCtrlLog::SetErrLog(0x8a,(int)(short)uVar1,0x3e2,(char *)(DAT_0002afb8 + 0x2af10));
          iVar3 = 0;
        }
        else {
          pcVar8 = (char *)*puVar7;
          uVar4 = GetDMMRetMsg(uVar1);
          MonCtrl::ConPrintfMessage(pcVar8,DAT_0002afbc + 0x2af26,uVar4,(uint)puVar2[3]);
          uVar9 = (uint)puVar2[3];
          iVar3 = 1 - uVar9;
          if (1 < uVar9) {
            iVar3 = 0;
          }
        }
        iVar5 = osal_free_msg(local_30,local_2c[0]);
        if (iVar5 != 0) {
          iVar3 = 0;
          puVar7 = *(undefined4 **)(iVar6 + DAT_0002af8c);
          MonCtrl::ConPrintfMessage((char *)*puVar7,DAT_0002afc0 + 0x2af56,iVar5);
          pcVar8 = (char *)*puVar7;
          uVar4 = GetOSALRetMsg(iVar5);
          MonCtrl::ConPrintfMessage(pcVar8,DAT_0002afc4 + 0x2af68,uVar4);
        }
        goto LAB_0002af6e;
      }
      puVar7 = *(undefined4 **)(iVar6 + DAT_0002af8c);
      MonCtrl::ConPrintfMessage((char *)*puVar7,DAT_0002afa8 + 0x2aeae,uVar4);
      pcVar8 = (char *)*puVar7;
      uVar4 = GetOSALRetMsg(uVar4);
      iVar6 = DAT_0002afac + 0x2aec0;
    }
    iVar3 = 0;
    MonCtrl::ConPrintfMessage(pcVar8,iVar6,uVar4);
  }
LAB_0002af6e:
  osal_dynamic_id(0x4a,0,local_30);
  return iVar3;
}


/* 0002afc8 */

/* DmmAccess::DmmFree(unsigned short) */

void DmmAccess::DmmFree(ushort param_1)

{
  MprCtrlLog::SetUnitHandleLog('x',param_1,0x393);
                    /* WARNING: Could not recover jumptable at 0x0001fcac. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*(code *)PTR_DmmCloseORFree_body_0004c270)(param_1,4,0);
  return;
}


/* 0002afe8 */

/* DmmAccess::DmmCloseAndFree(unsigned short) */

void DmmAccess::DmmCloseAndFree(ushort param_1)

{
  MprCtrlLog::SetUnitHandleLog('y',param_1,0x389);
                    /* WARNING: Could not recover jumptable at 0x0001fcac. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*(code *)PTR_DmmCloseORFree_body_0004c270)(param_1,4,2);
  return;
}


/* 0002b008 */

/* DmmAccess::DmmClose(unsigned short) */

void DmmAccess::DmmClose(ushort param_1)

{
  MprCtrlLog::SetUnitHandleLog('z',param_1,0x37f);
                    /* WARNING: Could not recover jumptable at 0x0001fcac. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*(code *)PTR_DmmCloseORFree_body_0004c270)(param_1,6,0);
  return;
}


/* 0002b028 */

/* DmmAccess::DmmAllocateNEWAndOpen_body(unsigned int, unsigned short, unsigned short, unsigned
   short) */

void * DmmAccess::DmmAllocateNEWAndOpen_body
                 (uint param_1,ushort param_2,ushort param_3,ushort param_4)

{
  short sVar1;
  bool bVar2;
  short *psVar3;
  int iVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  undefined4 *puVar7;
  int iVar8;
  uint uVar9;
  void *__dest;
  undefined4 *puVar10;
  char *pcVar11;
  size_t __size;
  undefined4 local_30;
  short *local_2c [2];
  
  local_30 = 0;
  local_2c[0] = (short *)0x0;
  iVar4 = osal_dynamic_id(0x2a,199,&local_30);
  iVar8 = DAT_0002b314 + 0x2b052;
  if (iVar4 != 0) {
    return (void *)0x0;
  }
  puVar7 = *(undefined4 **)(iVar8 + DAT_0002b318);
  MonCtrl::ConPrintfMessage((char *)*puVar7,DAT_0002b31c + 0x2b064,0);
  iVar4 = osal_valloc_msg_wait(DAT_0002b310,local_2c,0x18,0);
  MonCtrl::ConPrintfMessage((char *)*puVar7,DAT_0002b320 + 0x2b07e,local_2c[0]);
  psVar3 = local_2c[0];
  if (iVar4 != 0) {
    puVar10 = *(undefined4 **)(iVar8 + DAT_0002b324);
    MonCtrl::ConPrintfMessage((char *)*puVar10,DAT_0002b328 + 0x2b098,iVar4);
    pcVar11 = (char *)*puVar10;
    uVar5 = GetOSALRetMsg(iVar4);
    MonCtrl::ConPrintfMessage(pcVar11,DAT_0002b32c + 0x2b0ae,uVar5);
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
              ((char *)**(undefined4 **)(iVar8 + DAT_0002b324),DAT_0002b330 + 0x2b176,(uint)param_3)
    ;
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
  MonCtrl::ConPrintfMessage((char *)*puVar7,DAT_0002b334 + 0x2b182);
  if (bVar2) {
    iVar4 = osal_snd_msg(DAT_0002b310,local_2c[0]);
    if (iVar4 == 0) {
      MonCtrl::ConPrintfMessage((char *)*puVar7,DAT_0002b340 + 0x2b1c2);
    }
    else {
      puVar10 = *(undefined4 **)(iVar8 + DAT_0002b324);
      MonCtrl::ConPrintfMessage((char *)*puVar10,DAT_0002b338 + 0x2b19e,iVar4);
      pcVar11 = (char *)*puVar10;
      uVar5 = GetOSALRetMsg(iVar4);
      MonCtrl::ConPrintfMessage(pcVar11,DAT_0002b33c + 0x2b1b0,uVar5);
      bVar2 = false;
    }
  }
LAB_0002b1c4:
  MonCtrl::ConPrintfMessage((char *)*puVar7,DAT_0002b344 + 0x2b1cc);
  uVar5 = local_30;
  __dest = (void *)0x0;
  if (!bVar2) goto LAB_0002b3cc;
  MonCtrl::ConPrintfMessage((char *)*puVar7,DAT_0002b348 + 0x2b1e0);
  iVar4 = osal_rcv_msg_tmo(local_30,local_2c,0xffffffff);
  if (iVar4 == 0) {
    MonCtrl::ConPrintfMessage((char *)*puVar7,DAT_0002b354 + 0x2b224,uVar5);
    psVar3 = local_2c[0];
    sVar1 = *local_2c[0];
    if ((((sVar1 == -0x7fff) || (sVar1 == -0x7ffb)) || (sVar1 == -0x7ffd)) || (sVar1 == -0x7ffe)) {
      sVar1 = local_2c[0][1];
      iVar4 = CheckDMMRetCode(sVar1,(char *)0x0);
      if (iVar4 == 0) {
        puVar10 = *(undefined4 **)(iVar8 + DAT_0002b324);
        MonCtrl::ConPrintfMessage((char *)*puVar10,DAT_0002b36c + 0x2b2e0,(int)sVar1);
        pcVar11 = (char *)*puVar10;
        uVar6 = GetDMMRetMsg(sVar1);
        MonCtrl::ConPrintfMessage(pcVar11,DAT_0002b370 + 0x2b2f6,uVar6);
        MprCtrlLog::SetErrLog(0x89,(int)sVar1,0x326,(char *)(DAT_0002b374 + 0x2b30a));
        __dest = (void *)0x0;
      }
      else {
        pcVar11 = (char *)*puVar7;
        uVar6 = GetDMMRetMsg(sVar1);
        MonCtrl::ConPrintfMessage(pcVar11,DAT_0002b358 + 0x2b26a,uVar6);
        uVar9 = (uint)(ushort)psVar3[4];
        MonCtrl::ConPrintfMessage((char *)*puVar7,DAT_0002b35c + 0x2b27e,uVar9);
        MonCtrl::ConPrintfMessage((char *)*puVar7,DAT_0002b360 + 0x2b288,(uint)(ushort)psVar3[3]);
        MonCtrl::ConPrintfMessage((char *)*puVar7,DAT_0002b364 + 0x2b296,(uint)(ushort)psVar3[2]);
        if (uVar9 == 0) {
          __size = 0x18;
        }
        else {
          __size = (uVar9 + 2) * 8;
        }
        __dest = malloc(__size);
        memcpy(__dest,psVar3,__size);
        MonCtrl::ConPrintfMessage((char *)*puVar7,DAT_0002b368 + 0x2b2ca,__dest,__size,0x321);
      }
    }
    else {
      MonCtrl::ConPrintfMessage
                ((char *)**(undefined4 **)(iVar8 + DAT_0002b3e8),DAT_0002b3ec + 0x2b382);
      __dest = (void *)0x0;
    }
    iVar4 = osal_free_msg(uVar5,local_2c[0]);
    if (iVar4 == 0) goto LAB_0002b3cc;
    puVar10 = *(undefined4 **)(iVar8 + DAT_0002b3e8);
    MonCtrl::ConPrintfMessage((char *)*puVar10,DAT_0002b3f0 + 0x2b39e,iVar4);
    pcVar11 = (char *)*puVar10;
    uVar5 = GetOSALRetMsg(iVar4);
    MonCtrl::ConPrintfMessage(pcVar11,DAT_0002b3f4 + 0x2b3b0,uVar5);
    if (__dest == (void *)0x0) goto LAB_0002b3cc;
    MonCtrl::ConPrintfMessage((char *)*puVar7,DAT_0002b3f8 + 0x2b3c2,__dest);
    free(__dest);
  }
  else {
    puVar7 = *(undefined4 **)(iVar8 + DAT_0002b324);
    MonCtrl::ConPrintfMessage((char *)*puVar7,DAT_0002b34c + 0x2b200,iVar4);
    pcVar11 = (char *)*puVar7;
    uVar5 = GetOSALRetMsg(iVar4);
    MonCtrl::ConPrintfMessage(pcVar11,DAT_0002b350 + 0x2b212,uVar5);
  }
  __dest = (void *)0x0;
LAB_0002b3cc:
  osal_dynamic_id(0x4a,0,local_30);
  return __dest;
}


/* 0002b3fc */

/* DmmAccess::DmmShare(unsigned int, unsigned short) */

void * DmmAccess::DmmShare(uint param_1,ushort param_2)

{
  int iVar1;
  ushort uVar2;
  void *pvVar3;
  undefined4 *puVar4;
  
  iVar1 = DAT_0002b454;
  MprCtrlLog::SetUnitTypeLog(0x84,param_1,599);
  puVar4 = *(undefined4 **)(iVar1 + 0x2b418 + DAT_0002b458);
  MonCtrl::ConPrintfMessage((char *)*puVar4,DAT_0002b45c + 0x2b420,param_1);
  MonCtrl::ConPrintfMessage((char *)*puVar4,DAT_0002b460 + 0x2b42e,(uint)param_2);
  pvVar3 = (void *)DmmAllocateNEWAndOpen_body(param_1,param_2,2,0);
  if (pvVar3 != (void *)0x0) {
    uVar2 = DmmAccessPLA::GetUnitHandle(pvVar3);
    MprCtrlLog::SetUnitHandleLog(0x84,uVar2,0x25f);
  }
  return pvVar3;
}


/* 0002b464 */

/* DmmAccess::DmmShareAndOpen(unsigned int, unsigned short) */

void * DmmAccess::DmmShareAndOpen(uint param_1,ushort param_2)

{
  int iVar1;
  ushort uVar2;
  void *pvVar3;
  undefined4 *puVar4;
  
  iVar1 = DAT_0002b4bc;
  MprCtrlLog::SetUnitTypeLog(0x83,param_1,0x23e);
  puVar4 = *(undefined4 **)(iVar1 + 0x2b480 + DAT_0002b4c0);
  MonCtrl::ConPrintfMessage((char *)*puVar4,DAT_0002b4c4 + 0x2b488,param_1);
  MonCtrl::ConPrintfMessage((char *)*puVar4,DAT_0002b4c8 + 0x2b496,(uint)param_2);
  pvVar3 = (void *)DmmAllocateNEWAndOpen_body(param_1,param_2,2,1);
  if (pvVar3 != (void *)0x0) {
    uVar2 = DmmAccessPLA::GetUnitHandle(pvVar3);
    MprCtrlLog::SetUnitHandleLog(0x83,uVar2,0x246);
  }
  return pvVar3;
}


/* 0002b4cc */

/* DmmAccess::DmmReuseAndOpen(unsigned int, unsigned short) */

void * DmmAccess::DmmReuseAndOpen(uint param_1,ushort param_2)

{
  int iVar1;
  ushort uVar2;
  void *pvVar3;
  undefined4 *puVar4;
  
  iVar1 = DAT_0002b524;
  MprCtrlLog::SetUnitTypeLog(0x82,param_1,0x224);
  puVar4 = *(undefined4 **)(iVar1 + 0x2b4e8 + DAT_0002b528);
  MonCtrl::ConPrintfMessage((char *)*puVar4,DAT_0002b52c + 0x2b4f0,param_1);
  MonCtrl::ConPrintfMessage((char *)*puVar4,DAT_0002b530 + 0x2b4fe,(uint)param_2);
  pvVar3 = (void *)DmmAllocateNEWAndOpen_body(param_1,param_2,3,9);
  if (pvVar3 != (void *)0x0) {
    uVar2 = DmmAccessPLA::GetUnitHandle(pvVar3);
    MprCtrlLog::SetUnitHandleLog(0x82,uVar2,0x22d);
  }
  return pvVar3;
}


/* 0002b534 */

/* DmmAccess::DmmAllocateAndOpen(unsigned int) */

void * DmmAccess::DmmAllocateAndOpen(uint param_1)

{
  int iVar1;
  ushort uVar2;
  void *pvVar3;
  
  iVar1 = DAT_0002b580;
  MprCtrlLog::SetUnitTypeLog('u',param_1,0x20c);
  MonCtrl::ConPrintfMessage
            ((char *)**(undefined4 **)(iVar1 + 0x2b550 + DAT_0002b584),DAT_0002b588 + 0x2b556,
             param_1);
  pvVar3 = (void *)DmmAllocateNEWAndOpen_body(param_1,0,1,1);
  if (pvVar3 != (void *)0x0) {
    uVar2 = DmmAccessPLA::GetUnitHandle(pvVar3);
    MprCtrlLog::SetUnitHandleLog('u',uVar2,0x213);
  }
  return pvVar3;
}


/* 0002b58c */

/* DmmAccess::DmmAllocate(unsigned int) */

void * DmmAccess::DmmAllocate(uint param_1)

{
  int iVar1;
  ushort uVar2;
  void *pvVar3;
  
  iVar1 = DAT_0002b5d8;
  MprCtrlLog::SetUnitTypeLog('t',param_1,0x1f6);
  MonCtrl::ConPrintfMessage
            ((char *)**(undefined4 **)(iVar1 + 0x2b5a8 + DAT_0002b5dc),DAT_0002b5e0 + 0x2b5ae,
             param_1);
  pvVar3 = (void *)DmmAllocateNEWAndOpen_body(param_1,0,1,0);
  if (pvVar3 != (void *)0x0) {
    uVar2 = DmmAccessPLA::GetUnitHandle(pvVar3);
    MprCtrlLog::SetUnitHandleLog('t',uVar2,0x1fd);
  }
  return pvVar3;
}


/* 0002b5e4 */

/* DmmAccess::DmmOpen(unsigned short) */

void DmmAccess::DmmOpen(ushort param_1)

{
  int iVar1;
  
  iVar1 = DAT_0002b61c;
  MprCtrlLog::SetUnitHandleLog('v',param_1,0x1e4);
  MonCtrl::ConPrintfMessage
            ((char *)**(undefined4 **)(iVar1 + 0x2b600 + DAT_0002b620),DAT_0002b624 + 0x2b606,
             (uint)param_1);
  (*(code *)PTR_DmmAllocateNEWAndOpen_body_0004be58)(0,(uint)param_1,5,0);
  return;
}


/* 0002b628 */

/* DmmAccess::GetDmmExtList(DmmAccess::t_unitTypeConvertList*, unsigned short*) */

void * DmmAccess::GetDmmExtList(t_unitTypeConvertList *param_1,ushort *param_2)

{
  t_unitTypeConvertList *ptVar1;
  short sVar2;
  ushort uVar3;
  bool bVar4;
  short *psVar5;
  int iVar6;
  size_t sVar7;
  undefined4 uVar8;
  undefined4 uVar9;
  void *pvVar10;
  t_unitTypeConvertList *ptVar11;
  undefined4 *puVar12;
  uint uVar13;
  undefined4 *puVar14;
  uint uVar15;
  uint *puVar16;
  uint uVar17;
  int iVar18;
  int iVar19;
  char *pcVar20;
  uint uVar21;
  uint local_50;
  void *local_4c;
  uint local_48;
  int local_38;
  undefined4 local_30;
  short *local_2c [2];
  
  iVar19 = DAT_0002b8b4 + 0x2b63a;
  local_2c[0] = (short *)0x0;
  uVar17 = 0;
  local_30 = 0;
  ptVar11 = param_1;
  while (ptVar1 = ptVar11 + 10, ptVar11 = ptVar11 + 0xc, *(short *)ptVar1 != -1) {
    uVar17 = uVar17 + 1;
  }
  puVar14 = *(undefined4 **)(iVar19 + DAT_0002b8b8);
  MonCtrl::ConPrintfMessage((char *)*puVar14,DAT_0002b8bc + 0x2b664,uVar17);
  iVar6 = osal_dynamic_id(0x2a,199,&local_30);
  if (iVar6 == 0) {
    local_38 = 0;
    ptVar11 = param_1;
    for (uVar15 = 0; uVar15 < uVar17; uVar15 = uVar15 + 1) {
      if ((**(char **)(iVar19 + DAT_0002b8c0) == '\0') ||
         (((iVar6 = *(int *)ptVar11, iVar6 != DAT_0002b8ac && (iVar6 != 0x1bf)) && (iVar6 != 0x1be))
         )) {
        uVar9 = *(undefined4 *)ptVar11;
        MonCtrl::ConPrintfMessage
                  ((char *)*puVar14,DAT_0002b8c4 + 0x2b6c6,uVar15,uVar15 & 0xffff,uVar9);
        iVar6 = osal_valloc_msg_wait(DAT_0002b8b0,local_2c,0x18,0);
        MonCtrl::ConPrintfMessage((char *)*puVar14,DAT_0002b8c8 + 0x2b6e2,local_2c[0]);
        psVar5 = local_2c[0];
        if (iVar6 != 0) {
          MonCtrl::ConPrintfMessage
                    ((char *)**(undefined4 **)(iVar19 + DAT_0002b8cc),DAT_0002b8d0 + 0x2b702,iVar6,
                     *(undefined4 **)(iVar19 + DAT_0002b8cc),uVar9);
          break;
        }
        memset(local_2c[0],0,0x18);
        *psVar5 = 1;
        *(undefined4 *)(psVar5 + 2) = *(undefined4 *)ptVar11;
        psVar5[4] = 0;
        psVar5[5] = 0;
        psVar5[6] = -1;
        psVar5[7] = -1;
        FUN_0002a9c2(local_2c[0],local_30);
        iVar6 = DAT_0002b8d4;
        pcVar20 = (char *)*puVar14;
        psVar5[10] = (short)uVar15;
        psVar5[0xb] = 1;
        MonCtrl::ConPrintfMessage(pcVar20,iVar6 + 0x2b746);
        iVar6 = osal_snd_msg(DAT_0002b8b0,local_2c[0]);
        if (iVar6 != 0) {
          MonCtrl::ConPrintfMessage
                    ((char *)**(undefined4 **)(iVar19 + DAT_0002b8cc),DAT_0002b8d8 + 0x2b76c,iVar6);
          bVar4 = false;
          goto LAB_0002b792;
        }
        MonCtrl::ConPrintfMessage((char *)*puVar14,DAT_0002b8dc + 0x2b77a,0);
        *(short *)(ptVar11 + 10) = (short)uVar15;
      }
      else {
        *(undefined2 *)(ptVar11 + 10) = 0xffff;
        local_38 = local_38 + 1;
      }
      ptVar11 = ptVar11 + 0xc;
    }
    bVar4 = true;
LAB_0002b792:
    MonCtrl::ConPrintfMessage((char *)*puVar14,DAT_0002b8e0 + 0x2b79a);
    uVar9 = local_30;
    if (bVar4) {
      sVar7 = DmmAccessPLA::GetExtListPackHeaderSize(uVar17);
      local_4c = malloc(sVar7);
      sVar7 = DmmAccessPLA::GetExtListPackHeaderSize(uVar17);
      memset(local_4c,0,sVar7);
    }
    else {
      local_4c = (void *)0x0;
    }
    pcVar20 = (char *)*puVar14;
    uVar8 = DmmAccessPLA::GetExtListPackHeaderSize(uVar17);
    MonCtrl::ConPrintfMessage(pcVar20,DAT_0002b8e4 + 0x2b7d2,uVar8);
    MonCtrl::ConPrintfMessage((char *)*puVar14,DAT_0002b8e8 + 0x2b7e2,local_4c);
    uVar17 = uVar17 - local_38;
    if (bVar4) {
      uVar21 = 0;
      local_50 = 0;
      uVar15 = 0;
      bVar4 = false;
      for (local_48 = 0; local_48 < uVar17; local_48 = local_48 + 1) {
        MonCtrl::ConPrintfMessage((char *)*puVar14,DAT_0002b8ec + 0x2b818,local_48);
        iVar6 = osal_rcv_msg_tmo(local_30,local_2c,0xffffffff);
        if (iVar6 != 0) {
          puVar12 = *(undefined4 **)(iVar19 + DAT_0002b8cc);
          MonCtrl::ConPrintfMessage((char *)*puVar12,DAT_0002b8f0 + 0x2b842,iVar6);
          pcVar20 = (char *)*puVar12;
          uVar8 = GetOSALRetMsg(iVar6);
          iVar18 = DAT_0002b8f4 + 0x2b868;
          MonCtrl::ConPrintfMessage(pcVar20,iVar18,uVar8);
          iVar6 = osal_free_msg(uVar9,local_2c[0]);
          if (iVar6 != 0) {
            MonCtrl::ConPrintfMessage((char *)*puVar12,DAT_0002b8f8 + 0x2b886,0x116);
            pcVar20 = (char *)*puVar12;
            uVar9 = GetOSALRetMsg(iVar6);
            MonCtrl::ConPrintfMessage(pcVar20,iVar18,uVar9);
          }
          break;
        }
        MonCtrl::ConPrintfMessage((char *)*puVar14,DAT_0002bc44 + 0x2b904,uVar9);
        psVar5 = local_2c[0];
        sVar2 = local_2c[0][1];
        iVar6 = CheckDMMRetCode(sVar2,(char *)0x0);
        if (iVar6 == 0) {
          puVar12 = *(undefined4 **)(iVar19 + DAT_0002bc48);
          MonCtrl::ConPrintfMessage((char *)*puVar12,DAT_0002bc4c + 0x2b938,(int)sVar2);
          pcVar20 = (char *)*puVar12;
          uVar8 = GetDMMRetMsg(sVar2);
          MonCtrl::ConPrintfMessage(pcVar20,DAT_0002bc50 + 0x2b950,uVar8);
          uVar15 = 0;
          ptVar11 = param_1;
          do {
            if (*(short *)(ptVar11 + 10) == psVar5[3]) {
              MonCtrl::ConPrintfMessage
                        ((char *)*puVar12,DAT_0002bc54 + 0x2b978,*(undefined4 *)ptVar11);
              MprCtrlLog::SetErrLog('}',(int)sVar2,0x134,(char *)(DAT_0002bc58 + 0x2b986));
              MprCtrlLog::SetParamLog
                        ('}',0,(ushort)((uint)*(undefined4 *)ptVar11 >> 0x10),
                         (ushort)*(undefined4 *)ptVar11,0x135);
              break;
            }
            uVar15 = uVar15 + 1;
            ptVar11 = ptVar11 + 0xc;
          } while (uVar15 < uVar17);
          if (sVar2 != -3) {
            iVar19 = osal_free_msg(uVar9,local_2c[0]);
            if (iVar19 != 0) {
              MonCtrl::ConPrintfMessage((char *)*puVar12,DAT_0002bc60 + 0x2b9fc,0x146);
              pcVar20 = (char *)*puVar12;
              uVar9 = GetOSALRetMsg(iVar19);
              iVar19 = DAT_0002bc64 + 0x2ba14;
LAB_0002bafe:
              MonCtrl::ConPrintfMessage(pcVar20,iVar19,uVar9);
            }
            goto LAB_0002bb76;
          }
          if (*psVar5 == -0x7fff) {
            MonCtrl::ConPrintfMessage((char *)*puVar12,DAT_0002bc5c + 0x2b9d0);
            *(undefined2 *)(param_1 + uVar15 * 0xc + 10) = 0;
            *(undefined2 *)(param_1 + uVar15 * 0xc + 8) = 0;
          }
        }
        else if (*psVar5 == -0x7fff) {
          if (!bVar4) {
            local_50 = (uint)(ushort)psVar5[2];
            bVar4 = true;
          }
          uVar3 = psVar5[4];
          uVar13 = (uint)uVar3;
          MonCtrl::ConPrintfMessage((char *)*puVar14,DAT_0002bc68 + 0x2ba3e,uVar13);
          MonCtrl::ConPrintfMessage((char *)*puVar14,DAT_0002bc6c + 0x2ba48,(uint)(ushort)psVar5[3])
          ;
          MonCtrl::ConPrintfMessage((char *)*puVar14,DAT_0002bc70 + 0x2ba54,(uint)(ushort)psVar5[2])
          ;
          if (uVar13 != 0) {
            sVar7 = DmmAccessPLA::GetExtListPackSize(uVar13);
            pvVar10 = malloc(sVar7);
            DmmAccessPLA::SetExtListPackOnPackHeader(local_4c,pvVar10,uVar21);
            puVar16 = (uint *)(psVar5 + 8);
            for (uVar15 = 0; uVar15 < uVar13; uVar15 = uVar15 + 1) {
              DmmAccessPLA::SetExtListOnPack(pvVar10,*puVar16,puVar16[1],uVar15);
              puVar16 = puVar16 + 2;
            }
            uVar15 = 0;
            ptVar11 = param_1;
            do {
              if (*(short *)(ptVar11 + 10) == psVar5[3]) {
                *(undefined2 *)(ptVar11 + 10) = 0;
                break;
              }
              uVar15 = uVar15 + 1;
              ptVar11 = ptVar11 + 0xc;
            } while (uVar15 < uVar17);
            MonCtrl::ConPrintfMessage((char *)*puVar14,DAT_0002bc74 + 0x2baba,uVar15);
            if (uVar15 == uVar17) {
              iVar6 = osal_free_msg(uVar9,local_2c[0]);
              if (iVar6 != 0) {
                puVar12 = *(undefined4 **)(iVar19 + DAT_0002bc48);
                MonCtrl::ConPrintfMessage((char *)*puVar12,DAT_0002bc78 + 0x2bae6,0x173);
                pcVar20 = (char *)*puVar12;
                uVar9 = GetOSALRetMsg(iVar6);
                iVar19 = DAT_0002bc7c + 0x2bafc;
                goto LAB_0002bafe;
              }
              goto LAB_0002bb76;
            }
            iVar6 = uVar15 * 0xc;
            uVar21 = uVar21 + 1;
            DmmAccessPLA::SetExtListPackStatus
                      (pvVar10,*(uint *)(param_1 + iVar6 + 4),uVar3,psVar5[2],
                       *(uint *)(param_1 + iVar6));
            *(short *)(param_1 + iVar6 + 8) = psVar5[2];
          }
        }
        iVar6 = osal_free_msg(uVar9,local_2c[0]);
        if (iVar6 != 0) {
          puVar12 = *(undefined4 **)(iVar19 + DAT_0002bc48);
          MonCtrl::ConPrintfMessage((char *)*puVar12,DAT_0002bc80 + 0x2bb48,0x186);
          pcVar20 = (char *)*puVar12;
          uVar8 = GetOSALRetMsg(iVar6);
          MonCtrl::ConPrintfMessage(pcVar20,DAT_0002bc84 + 0x2bb58,uVar8);
        }
      }
      for (uVar13 = 0; uVar13 < uVar17; uVar13 = uVar13 + 1) {
        if (*(short *)(param_1 + uVar15 * 0xc + 8) == 0) {
          MonCtrl::ConPrintfMessage
                    ((char *)**(undefined4 **)(iVar19 + DAT_0002bc48),DAT_0002bc88 + 0x2bb90,uVar15)
          ;
          break;
        }
      }
      DmmAccessPLA::SetExtListPackHeaderStatus(local_4c,(ushort)local_50,(ushort)uVar21);
      iVar19 = DAT_0002bc94;
      pcVar20 = (char *)*puVar14;
      *param_2 = (ushort)local_50;
      MonCtrl::ConPrintfMessage(pcVar20,iVar19 + 0x2bc32);
      MonCtrl::ConPrintfMessage((char *)*puVar14,DAT_0002bc98 + 0x2bc3c,local_50);
    }
    else {
LAB_0002bb76:
      if (local_4c != (void *)0x0) {
        for (uVar15 = 0; uVar15 < uVar17; uVar15 = uVar15 + 1) {
          iVar19 = DmmAccessPLA::GetExtListPackAdrsOnPackHeader(local_4c,uVar15);
          if (iVar19 != 0) {
            pcVar20 = (char *)*puVar14;
            uVar9 = DmmAccessPLA::GetExtListPackAdrsOnPackHeader(local_4c,uVar15);
            MonCtrl::ConPrintfMessage(pcVar20,DAT_0002bc8c + 0x2bbbe,uVar9,uVar15);
            pvVar10 = (void *)DmmAccessPLA::GetExtListPackAdrsOnPackHeader(local_4c,uVar15);
            free(pvVar10);
          }
        }
        MonCtrl::ConPrintfMessage((char *)*puVar14,DAT_0002bc90 + 0x2bbe2,local_4c);
        free(local_4c);
        local_4c = (void *)0x0;
      }
    }
    osal_dynamic_id(0x4a,0,local_30);
  }
  else {
    local_4c = (void *)0x0;
  }
  return local_4c;
}


/* 0002bc9c */

/* DmmAccess::AllocDmmMemory(int, unsigned short*) */

undefined4 DmmAccess::AllocDmmMemory(int param_1,ushort *param_2)

{
  t_unitTypeConvertList *ptVar1;
  undefined4 uVar2;
  int iVar3;
  
  MprCtrlLog::SetStartApiLog(0x80,0x60b);
  ptVar1 = (t_unitTypeConvertList *)UnitTypeTableSelect(param_1);
  iVar3 = DAT_0002bd20 + 0x2bcbc;
  MprCtrlLog::SetMemoryMapLog(param_1);
  MonCtrl::ConPrintfMessage
            ((char *)**(undefined4 **)(iVar3 + DAT_0002bd24),DAT_0002bd28 + 0x2bcce,param_1,ptVar1);
  if (param_1 < 0x1a) {
    if (ptVar1 == (t_unitTypeConvertList *)0x0) {
      MonCtrl::ConPrintfMessage
                ((char *)**(undefined4 **)(iVar3 + DAT_0002bd30),DAT_0002bd34 + 0x2bcf8);
      uVar2 = 0;
    }
    else {
      uVar2 = GetDmmExtList(ptVar1,param_2);
      *(undefined4 *)(*(int *)(iVar3 + DAT_0002bd2c) + param_1 * 4) = uVar2;
    }
  }
  else {
    uVar2 = 0;
    MonCtrl::ConPrintfMessage
              ((char *)**(undefined4 **)(iVar3 + DAT_0002bd30),DAT_0002bd38 + 0x2bd0a);
  }
  MprCtrlLog::SetEndApiLog(0x80,0,0x623);
  return uVar2;
}


/* 0002bd3c */

/* DmmAccess::IsRemainMemory(DmmAccess::t_unitTypeConvertList*) */

undefined4 DmmAccess::IsRemainMemory(t_unitTypeConvertList *param_1)

{
  t_unitTypeConvertList *ptVar1;
  
  do {
    if (*(short *)(param_1 + 10) == -1) {
      return 0;
    }
    ptVar1 = param_1 + 8;
    param_1 = param_1 + 0xc;
  } while (*(short *)ptVar1 == 0);
  return 1;
}


/* 0002bd5c */

/* DmmAccess::CnvAreaId2ModeSubArea(unsigned int) */

undefined4 DmmAccess::CnvAreaId2ModeSubArea(uint param_1)

{
  if (param_1 < 10) {
    return *(undefined4 *)(DAT_0002bd74 + 0x2bd6a + param_1 * 4);
  }
  return 0;
}


/* 0002bd78 */

/* DmmAccess::FreeDmmExtList(DmmAccess::t_unitTypeConvertList*, unsigned int) */

undefined4 DmmAccess::FreeDmmExtList(t_unitTypeConvertList *param_1,uint param_2)

{
  t_unitTypeConvertList *ptVar1;
  uint uVar2;
  int iVar3;
  t_unitTypeConvertList *ptVar4;
  uint uVar5;
  int iVar6;
  uint uVar7;
  undefined4 uVar8;
  
  iVar6 = DAT_0002bdf4 + 0x2bd8a;
  uVar7 = 0;
  ptVar4 = param_1;
  while (ptVar1 = ptVar4 + 10, ptVar4 = ptVar4 + 0xc, *(short *)ptVar1 != -1) {
    uVar7 = uVar7 + 1;
  }
  uVar8 = 1;
  for (uVar5 = 0; uVar5 < uVar7; uVar5 = uVar5 + 1) {
    if (*(short *)(param_1 + 8) == 0) {
      MonCtrl::ConPrintfMessage
                ((char *)**(undefined4 **)(iVar6 + DAT_0002bdf8),DAT_0002bdfc + 0x2bdd8,uVar5);
      *(undefined2 *)(param_1 + 10) = 0;
    }
    else {
      uVar2 = CnvAreaId2ModeSubArea(*(uint *)(param_1 + 4));
      if ((uVar2 & param_2) != 0) {
        iVar3 = DmmCloseAndFree(*(ushort *)(param_1 + 8));
        if (iVar3 == 0) {
          uVar8 = 0;
        }
        else {
          *(undefined2 *)(param_1 + 8) = 0;
          *(undefined2 *)(param_1 + 10) = 0;
        }
      }
    }
    param_1 = param_1 + 0xc;
  }
  return uVar8;
}


/* 0002be00 */

/* DmmAccess::FreeDmmMemory(int, unsigned int) */

undefined4 DmmAccess::FreeDmmMemory(int param_1,uint param_2)

{
  t_unitTypeConvertList *ptVar1;
  int iVar2;
  int iVar3;
  undefined4 *__ptr;
  undefined4 uVar4;
  uint uVar5;
  undefined4 *puVar6;
  undefined4 *puVar7;
  
  MprCtrlLog::SetStartApiLog(0x81,0x63c);
  ptVar1 = (t_unitTypeConvertList *)UnitTypeTableSelect(param_1);
  iVar3 = DAT_0002bf28 + 0x2be22;
  MprCtrlLog::SetMemoryMapLog(param_1);
  MprCtrlLog::SetParamLog(0x81,0,(ushort)(param_2 >> 0x10),(ushort)param_2,0x644);
  puVar6 = *(undefined4 **)(iVar3 + DAT_0002bf2c);
  MonCtrl::ConPrintfMessage((char *)*puVar6,DAT_0002bf30 + 0x2be48,param_1,param_2);
  if (param_1 < 0x1a) {
    if (ptVar1 == (t_unitTypeConvertList *)0x0) {
      MonCtrl::ConPrintfMessage
                ((char *)**(undefined4 **)(iVar3 + DAT_0002bf34),DAT_0002bf3c + 0x2be86,param_1);
      uVar4 = 0;
    }
    else {
      iVar2 = FreeDmmExtList(ptVar1,param_2);
      if (iVar2 == 0) {
        MonCtrl::ConPrintfMessage
                  ((char *)**(undefined4 **)(iVar3 + DAT_0002bf34),DAT_0002bf38 + 0x2be72);
        uVar4 = 0;
      }
      else {
        uVar4 = 1;
      }
    }
    iVar2 = *(int *)(iVar3 + DAT_0002bf40);
    if (*(int *)(iVar2 + param_1 * 4) == 0) {
      MonCtrl::ConPrintfMessage
                ((char *)**(undefined4 **)(iVar3 + DAT_0002bf34),DAT_0002bf4c + 0x2bef8,param_1);
    }
    else {
      iVar3 = IsRemainMemory(ptVar1);
      if (iVar3 == 0) {
        __ptr = *(undefined4 **)(iVar2 + param_1 * 4);
        puVar7 = __ptr;
        for (uVar5 = 0; uVar5 < *(ushort *)((int)__ptr + 2); uVar5 = uVar5 + 1) {
          MonCtrl::ConPrintfMessage((char *)*puVar6,DAT_0002bf44 + 0x2bec0,puVar7[1]);
          puVar7 = puVar7 + 1;
          free((void *)*puVar7);
        }
        MonCtrl::ConPrintfMessage((char *)*puVar6,DAT_0002bf48 + 0x2bedc,__ptr);
        free(__ptr);
        *(undefined4 *)(iVar2 + param_1 * 4) = 0;
      }
    }
  }
  else {
    uVar4 = 1;
    MonCtrl::ConPrintfMessage
              ((char *)**(undefined4 **)(iVar3 + DAT_0002bf34),DAT_0002bf50 + 0x2bf0c,param_1);
  }
  MprCtrlLog::SetEndApiLog(0x81,0,0x66b);
  return uVar4;
}


/* 0002bf54 */

/* DmmAccess::FreeDmmMemory(int) */

void DmmAccess::FreeDmmMemory(int param_1)

{
  (*(code *)PTR_FreeDmmMemory_0004bcec)(param_1,7);
  return;
}


/* 0002bf62 */

/* DmmAccess::FreeDmmExtFromHandle(unsigned short) */

void DmmAccess::FreeDmmExtFromHandle(ushort param_1)

{
  t_unitTypeConvertList atStack_28 [8];
  ushort local_20;
  undefined2 local_12;
  
  memset(atStack_28,0,0x18);
  local_12 = 0xffff;
  local_20 = param_1;
  FreeDmmExtList(atStack_28,7);
  return;
}


/* 0002bf8c */

/* DmmAccess::DmmHotPlug(unsigned int) */

int DmmAccess::DmmHotPlug(uint param_1)

{
  ushort uVar1;
  ushort *puVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  undefined4 uVar6;
  uint uVar7;
  int iVar8;
  undefined4 *puVar9;
  char *pcVar10;
  undefined4 *puVar11;
  undefined4 local_28;
  ushort *local_24 [2];
  
  MprCtrlLog::SetStartApiLog('{',0x6b4);
  local_28 = 0;
  local_24[0] = (ushort *)0x0;
  iVar3 = osal_dynamic_id(0x2a,199,&local_28);
  iVar8 = DAT_0002c1a0 + 0x2bfc0;
  if (iVar3 != 0) {
    return 0;
  }
  iVar3 = osal_valloc_msg_wait(DAT_0002c19c,local_24,0x18,0);
  puVar11 = *(undefined4 **)(iVar8 + DAT_0002c1a4);
  MonCtrl::ConPrintfMessage((char *)*puVar11,DAT_0002c1a8 + 0x2bfe0,local_24[0]);
  puVar2 = local_24[0];
  if (iVar3 == 0) {
    memset(local_24[0],0,0x18);
    iVar3 = DAT_0002c1b8;
    *(uint *)(puVar2 + 2) = param_1;
    *puVar2 = 0x15;
    puVar2[10] = 0;
    puVar2[6] = 0xffff;
    puVar2[7] = 0xffff;
    MonCtrl::ConPrintfMessage((char *)*puVar11,iVar3 + 0x2c02c);
    FUN_0002a9c2(local_24[0],local_28);
    iVar3 = osal_snd_msg(DAT_0002c19c,local_24[0]);
    if (iVar3 == 0) {
      iVar3 = 1;
      MonCtrl::ConPrintfMessage((char *)*puVar11,DAT_0002c1c4 + 0x2c084);
    }
    else {
      puVar9 = *(undefined4 **)(iVar8 + DAT_0002c1ac);
      MonCtrl::ConPrintfMessage((char *)*puVar9,DAT_0002c1bc + 0x2c05c,iVar3);
      pcVar10 = (char *)*puVar9;
      uVar4 = GetOSALRetMsg(iVar3);
      MonCtrl::ConPrintfMessage(pcVar10,DAT_0002c1c0 + 0x2c070,uVar4);
      iVar3 = 0;
    }
  }
  else {
    puVar9 = *(undefined4 **)(iVar8 + DAT_0002c1ac);
    MonCtrl::ConPrintfMessage((char *)*puVar9,DAT_0002c1b0 + 0x2bffa,iVar3);
    pcVar10 = (char *)*puVar9;
    uVar4 = GetOSALRetMsg(iVar3);
    MonCtrl::ConPrintfMessage(pcVar10,DAT_0002c1b4 + 0x2c00c,uVar4);
    iVar3 = 0;
  }
  MonCtrl::ConPrintfMessage((char *)*puVar11,DAT_0002c1c8 + 0x2c090);
  uVar4 = local_28;
  if (iVar3 == 0) goto LAB_0002c174;
  MonCtrl::ConPrintfMessage((char *)*puVar11,DAT_0002c1cc + 0x2c0a4);
  iVar5 = osal_rcv_msg_tmo(local_28,local_24,0xffffffff);
  puVar9 = *(undefined4 **)(iVar8 + DAT_0002c1ac);
  if (iVar5 == 0) {
    MonCtrl::ConPrintfMessage((char *)*puVar11,DAT_0002c1d8 + 0x2c0e4,uVar4);
    uVar7 = (uint)*local_24[0];
    uVar1 = local_24[0][1];
    if (uVar7 == 0x8015) {
      iVar8 = CheckDMMRetCode(uVar1,(char *)0x0);
      if (iVar8 == 0) {
        MonCtrl::ConPrintfMessage((char *)*puVar9,DAT_0002c1e0 + 0x2c126,(int)(short)uVar1);
        pcVar10 = (char *)*puVar9;
        uVar7 = GetDMMRetMsg(uVar1);
        iVar8 = DAT_0002c1e4 + 0x2c136;
        goto LAB_0002c140;
      }
      pcVar10 = (char *)*puVar9;
      uVar6 = GetDMMRetMsg(uVar1);
      MonCtrl::ConPrintfMessage(pcVar10,DAT_0002c1dc + 0x2c114,uVar6);
    }
    else {
      pcVar10 = (char *)*puVar9;
      iVar8 = DAT_0002c1e8 + 0x2c142;
LAB_0002c140:
      iVar3 = 0;
      MonCtrl::ConPrintfMessage(pcVar10,iVar8,uVar7);
    }
    iVar8 = osal_free_msg(uVar4,local_24[0]);
    if (iVar8 == 0) goto LAB_0002c174;
    MonCtrl::ConPrintfMessage((char *)*puVar9,DAT_0002c1ec + 0x2c15c,iVar8);
    pcVar10 = (char *)*puVar9;
    uVar4 = GetOSALRetMsg(iVar8);
    iVar3 = DAT_0002c1f0 + 0x2c16c;
  }
  else {
    MonCtrl::ConPrintfMessage((char *)*puVar9,DAT_0002c1d0 + 0x2c0c4,iVar5);
    pcVar10 = (char *)*puVar9;
    uVar4 = GetOSALRetMsg(iVar5);
    iVar3 = DAT_0002c1d4 + 0x2c0d4;
  }
  MonCtrl::ConPrintfMessage(pcVar10,iVar3,uVar4);
  iVar3 = 0;
LAB_0002c174:
  osal_dynamic_id(0x4a,0,local_28);
  MprCtrlLog::SetEndApiLog('{',0,0x722);
  return iVar3;
}


/* 0002c1f4 */

/* DmmAccess::DmmHotRemove(unsigned int) */

int DmmAccess::DmmHotRemove(uint param_1)

{
  short sVar1;
  undefined2 *puVar2;
  int iVar3;
  undefined4 uVar4;
  char *pcVar5;
  int iVar6;
  undefined4 *puVar7;
  undefined4 local_28;
  undefined2 *local_24 [2];
  
  MprCtrlLog::SetStartApiLog('|',0x72c);
  local_28 = 0;
  local_24[0] = (undefined2 *)0x0;
  iVar3 = osal_dynamic_id(0x2a,199,&local_28);
  iVar6 = DAT_0002c3b0 + 0x2c228;
  if (iVar3 != 0) {
    return 0;
  }
  uVar4 = osal_valloc_msg_wait(DAT_0002c3ac,local_24,0x18,0);
  iVar3 = CheckOSALRetCode(uVar4,0);
  puVar2 = local_24[0];
  puVar7 = *(undefined4 **)(iVar6 + DAT_0002c3b4);
  if (iVar3 == 0) {
    MonCtrl::ConPrintfMessage((char *)*puVar7,DAT_0002c3b8 + 0x2c252);
    pcVar5 = (char *)*puVar7;
    uVar4 = GetOSALRetMsg(uVar4);
    MonCtrl::ConPrintfMessage(pcVar5,DAT_0002c3bc + 0x2c262,uVar4);
    iVar3 = 0;
  }
  else {
    memset(local_24[0],0,0x18);
    *(uint *)(puVar2 + 2) = param_1;
    *puVar2 = 0x16;
    puVar2[10] = 0;
    FUN_0002a9c2(local_24[0],local_28);
    uVar4 = osal_snd_msg(DAT_0002c3ac,local_24[0]);
    iVar3 = CheckOSALRetCode(uVar4,0);
    if (iVar3 == 0) {
      MonCtrl::ConPrintfMessage((char *)*puVar7,DAT_0002c3c0 + 0x2c2ae,uVar4);
      pcVar5 = (char *)*puVar7;
      uVar4 = GetOSALRetMsg(uVar4);
      iVar6 = DAT_0002c3c4 + 0x2c2be;
    }
    else {
      uVar4 = osal_rcv_msg_tmo(local_28,local_24,0xffffffff);
      iVar3 = CheckOSALRetCode(uVar4,0);
      puVar2 = local_24[0];
      if (iVar3 != 0) {
        sVar1 = local_24[0][1];
        iVar3 = CheckDMMRetCode(sVar1,(char *)0x0);
        if (iVar3 == 0) {
          MonCtrl::ConPrintfMessage((char *)*puVar7,DAT_0002c3d0 + 0x2c31c,(int)sVar1);
          pcVar5 = (char *)*puVar7;
          uVar4 = GetDMMRetMsg(sVar1);
          MonCtrl::ConPrintfMessage(pcVar5,DAT_0002c3d4 + 0x2c32e,uVar4);
          iVar3 = 0;
        }
        else {
          pcVar5 = (char *)*puVar7;
          uVar4 = GetDMMRetMsg(sVar1);
          MonCtrl::ConPrintfMessage(pcVar5,DAT_0002c3d8 + 0x2c344,uVar4);
          iVar3 = 1 - (uint)(ushort)puVar2[3];
          if (1 < (ushort)puVar2[3]) {
            iVar3 = 0;
          }
        }
        iVar6 = osal_free_msg(local_28,local_24[0]);
        if (iVar6 != 0) {
          MonCtrl::ConPrintfMessage((char *)*puVar7,DAT_0002c3dc + 0x2c36c,iVar6);
          pcVar5 = (char *)*puVar7;
          uVar4 = GetOSALRetMsg(iVar6);
          MonCtrl::ConPrintfMessage(pcVar5,DAT_0002c3e0 + 0x2c37c,uVar4);
          iVar3 = 0;
        }
        goto LAB_0002c384;
      }
      MonCtrl::ConPrintfMessage((char *)*puVar7,DAT_0002c3c8 + 0x2c2e4,uVar4);
      pcVar5 = (char *)*puVar7;
      uVar4 = GetOSALRetMsg(uVar4);
      iVar6 = DAT_0002c3cc + 0x2c2f4;
    }
    iVar3 = 0;
    MonCtrl::ConPrintfMessage(pcVar5,iVar6,uVar4);
  }
LAB_0002c384:
  osal_dynamic_id(0x4a,0,local_28);
  MprCtrlLog::SetEndApiLog('|',0,0x786);
  return iVar3;
}


/* 0002c3e4 */

/* DmmAccess::GetModeIdName(int) */

undefined * DmmAccess::GetModeIdName(int param_1)

{
  switch(param_1) {
  case 0:
    return (undefined *)(DAT_0002c48c + 0x2c40c);
  case 1:
    return &UNK_0002c48a + DAT_0002c4e0;
  case 2:
    return (undefined *)(DAT_0002c490 + 0x2c412);
  case 3:
    return (undefined *)(DAT_0002c494 + 0x2c418);
  case 4:
    return (undefined *)(DAT_0002c498 + 0x2c41e);
  case 5:
    return (undefined *)(DAT_0002c49c + 0x2c424);
  case 6:
    return (undefined *)(DAT_0002c4a0 + 0x2c42a);
  case 7:
    return (undefined *)(DAT_0002c4a4 + 0x2c430);
  case 8:
    return (undefined *)(DAT_0002c4a8 + 0x2c436);
  case 9:
    return (undefined *)(DAT_0002c4ac + 0x2c43c);
  case 10:
    return (undefined *)(DAT_0002c4b0 + 0x2c442);
  case 0xb:
    return (undefined *)(DAT_0002c4b4 + 0x2c448);
  case 0xc:
    return (undefined *)(DAT_0002c4b8 + 0x2c44e);
  case 0xd:
    return (undefined *)(DAT_0002c4bc + 0x2c454);
  case 0xe:
    return (undefined *)(DAT_0002c4c0 + 0x2c45a);
  case 0xf:
    return (undefined *)(DAT_0002c4c4 + 0x2c460);
  case 0x10:
    return (undefined *)(DAT_0002c4c8 + 0x2c466);
  case 0x11:
    return (undefined *)(DAT_0002c4cc + 0x2c46c);
  default:
    return (undefined *)(DAT_0002c4dc + 0x2c484);
  case 0x13:
    return (undefined *)(DAT_0002c4d0 + 0x2c472);
  case 0x14:
    return (undefined *)(DAT_0002c4d4 + 0x2c478);
  case 0x15:
    return (undefined *)(DAT_0002c4d8 + 0x2c47e);
  }
}


/* 0002c4e4 */

/* DmmAccess::PrintModeTable(int) */

void DmmAccess::PrintModeTable(int param_1)

{
  short *psVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;
  undefined4 *puVar4;
  uint uVar5;
  char *pcVar6;
  uint uVar7;
  
  puVar2 = (undefined4 *)UnitTypeTableSelect(param_1);
  if (puVar2 != (undefined4 *)0x0) {
    puVar4 = *(undefined4 **)(DAT_0002c56c + 0x2c4f8 + DAT_0002c570);
    pcVar6 = (char *)*puVar4;
    GetModeIdName(param_1);
    MonCtrl::ConPutMessage(pcVar6);
    uVar7 = 0;
    MonCtrl::ConPutMessage((char *)*puVar4);
    MonCtrl::ConPutMessage((char *)*puVar4);
    puVar3 = puVar2;
    while (psVar1 = (short *)((int)puVar3 + 10), puVar3 = puVar3 + 3, *psVar1 != -1) {
      uVar7 = uVar7 + 1;
    }
    for (uVar5 = 0; uVar5 < uVar7; uVar5 = uVar5 + 1) {
      MonCtrl::ConPrintfMessage
                ((char *)*puVar4,DAT_0002c57c + 0x2c54c,*puVar2,puVar2[1],
                 (uint)*(ushort *)(puVar2 + 2),(uint)*(ushort *)((int)puVar2 + 10));
      puVar2 = puVar2 + 3;
    }
  }
  return;
}


/* 0002c580 */

/* DmmAccess::PrintAllModeTable() */

void DmmAccess::PrintAllModeTable(void)

{
  int iVar1;
  int iVar2;
  
  iVar1 = 0;
  do {
    iVar2 = iVar1 + 1;
    PrintModeTable(iVar1);
    iVar1 = iVar2;
  } while (iVar2 != 0x1a);
  return;
}


/* 0002c594 */

/* DmmAccessPLA::GetUnitHandle(void*) */

undefined2 DmmAccessPLA::GetUnitHandle(void *param_1)

{
  return *(undefined2 *)((int)param_1 + 4);
}


/* 0002c5a2 */

/* DmmAccessPLA::GetExtListCount(void*) */

undefined2 DmmAccessPLA::GetExtListCount(void *param_1)

{
  return *(undefined2 *)((int)param_1 + 8);
}


/* 0002c5b0 */

/* DmmAccessPLA::GetExtListTop(void*) */

int DmmAccessPLA::GetExtListTop(void *param_1)

{
  return (int)param_1 + 0x10;
}


/* 0002c5b8 */

/* DmmAccessPLA::GetExtListPackHeaderSize(unsigned int) */

int DmmAccessPLA::GetExtListPackHeaderSize(uint param_1)

{
  return (param_1 + 1) * 4;
}


/* 0002c5c2 */

/* DmmAccessPLA::GetExtListPackSize(unsigned int) */

int DmmAccessPLA::GetExtListPackSize(uint param_1)

{
  return (param_1 + 2) * 8;
}


/* 0002c5cc */

/* DmmAccessPLA::SetExtListPackHeaderStatus(void*, unsigned short, unsigned short) */

void DmmAccessPLA::SetExtListPackHeaderStatus(void *param_1,ushort param_2,ushort param_3)

{
  *(ushort *)param_1 = param_2;
  *(ushort *)((int)param_1 + 2) = param_3;
  return;
}


/* 0002c5d6 */

/* DmmAccessPLA::SetExtListPackOnPackHeader(void*, void*, unsigned int) */

void DmmAccessPLA::SetExtListPackOnPackHeader(void *param_1,void *param_2,uint param_3)

{
  *(void **)((int)param_1 + param_3 * 4 + 4) = param_2;
  return;
}


/* 0002c5e2 */

/* DmmAccessPLA::GetExtListPackAdrsOnPackHeader(void*, unsigned int) */

undefined4 DmmAccessPLA::GetExtListPackAdrsOnPackHeader(void *param_1,uint param_2)

{
  return *(undefined4 *)((int)param_1 + param_2 * 4 + 4);
}


/* 0002c5ee */

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


/* 0002c5fe */

/* DmmAccessPLA::SetExtListOnPack(void*, unsigned int, unsigned int, unsigned int) */

void DmmAccessPLA::SetExtListOnPack(void *param_1,uint param_2,uint param_3,uint param_4)

{
  *(uint *)((int)param_1 + (param_4 + 2) * 8) = param_2;
  *(uint *)((int)param_1 + (param_4 + 2) * 8 + 4) = param_3;
  return;
}


/* 0002c610 */

/* DmmAccessPLA::GetExtCountFromDmmAlloc(void*) */

undefined2 DmmAccessPLA::GetExtCountFromDmmAlloc(void *param_1)

{
  return *(undefined2 *)((int)param_1 + 8);
}


/* 0002c618 */

/* DmmAccessPLA::GetExtCountFromDmmOpen(void*) */

undefined2 DmmAccessPLA::GetExtCountFromDmmOpen(void *param_1)

{
  return *(undefined2 *)((int)param_1 + 8);
}


/* 0002c620 */

/* DmmAccessPLA::GetExtAdrsFromDmmAlloc(void*, unsigned short) */

undefined4 DmmAccessPLA::GetExtAdrsFromDmmAlloc(void *param_1,ushort param_2)

{
  return *(undefined4 *)((int)param_1 + (uint)param_2 * 8 + 0x10);
}


/* 0002c62c */

/* DmmAccessPLA::GetExtAdrsFromDmmOpen(void*, unsigned short) */

undefined4 DmmAccessPLA::GetExtAdrsFromDmmOpen(void *param_1,ushort param_2)

{
  return *(undefined4 *)((int)param_1 + (uint)param_2 * 8 + 0x10);
}


/* 0002c638 */

/* DmmAccessPLA::GetExtSizeFromDmmAlloc(void*, unsigned short) */

undefined4 DmmAccessPLA::GetExtSizeFromDmmAlloc(void *param_1,ushort param_2)

{
  return *(undefined4 *)((int)param_1 + (uint)param_2 * 8 + 0x14);
}


/* 0002c644 */

/* DmmAccessPLA::GetExtSizeFromDmmOpen(void*, unsigned short) */

undefined4 DmmAccessPLA::GetExtSizeFromDmmOpen(void *param_1,ushort param_2)

{
  return *(undefined4 *)((int)param_1 + (uint)param_2 * 8 + 0x14);
}


/* 0002c650 */

/* DmmAccessPLA::GetUnitHandleFromDmmAlloc(void*) */

undefined2 DmmAccessPLA::GetUnitHandleFromDmmAlloc(void *param_1)

{
  return *(undefined2 *)((int)param_1 + 4);
}


/* 0002c658 */

/* EventSwitcher::~EventSwitcher() */

EventSwitcher * __thiscall EventSwitcher::~EventSwitcher(EventSwitcher *this)

{
  _utlCell *p_Var1;
  _utlCell *p_Var2;
  
  *(int *)this = *(int *)(DAT_0002c6cc + 0x2c66a + DAT_0002c6d0) + 8;
  while (p_Var2 = (_utlCell *)UtilList::GetTopCellFromList((_utlList *)(this + 4)),
        p_Var2 != (_utlCell *)0x0) {
    UtilList::RemoveCellFromList((_utlList *)(this + 4),p_Var2);
    while (p_Var1 = (_utlCell *)UtilList::GetTopCellFromList((_utlList *)(p_Var2 + 0xc)),
          p_Var1 != (_utlCell *)0x0) {
      UtilList::RemoveCellFromList((_utlList *)(p_Var2 + 0xc),p_Var1);
      if (*(void **)(p_Var1 + 0xc) != (void *)0x0) {
        operator_delete__(*(void **)(p_Var1 + 0xc));
      }
      operator_delete(p_Var1);
    }
    operator_delete(p_Var2);
  }
  if (*(int **)(this + 0x10) != (int *)0x0) {
    (**(code **)(**(int **)(this + 0x10) + 4))();
    *(undefined4 *)(this + 0x10) = 0;
  }
  return this;
}


/* 0002c6d4 */

/* EventSwitcher::~EventSwitcher() */

EventSwitcher * __thiscall EventSwitcher::~EventSwitcher(EventSwitcher *this)

{
  ~EventSwitcher(this);
  operator_delete(this);
  return this;
}


/* 0002c6e8 */

/* EventSwitcher::EventSwitcher() */

EventSwitcher * __thiscall EventSwitcher::EventSwitcher(EventSwitcher *this)

{
  ObjLock *this_00;
  
  *(int *)this = *(int *)(DAT_0002c720 + 0x2c6f0 + DAT_0002c724) + 8;
  this_00 = operator_new(0x1c);
  MWF::ObjLock::ObjLock(this_00);
  *(ObjLock **)(this + 0x10) = this_00;
  MemUtil::MemSet8(this + 4,'\0',0xc);
  return this;
}


/* 0002c728 */

/* EventSwitcher::SearchInstanceCell(void*) */

void __thiscall EventSwitcher::SearchInstanceCell(EventSwitcher *this,void *param_1)

{
  _utlCell *p_Var1;
  
  for (p_Var1 = (_utlCell *)UtilList::GetTopCellFromList((_utlList *)(this + 4));
      (p_Var1 != (_utlCell *)0x0 && (*(void **)(p_Var1 + 8) != param_1));
      p_Var1 = (_utlCell *)UtilList::GetNextCell(p_Var1)) {
  }
  return;
}


/* 0002c746 */

/* EventSwitcher::DeleteAllCallbackFunc(void*) */

void __thiscall EventSwitcher::DeleteAllCallbackFunc(EventSwitcher *this,void *param_1)

{
  int iVar1;
  _utlCell *p_Var2;
  
  MWF::ObjLock::Lock(*(ObjLock **)(this + 0x10));
  iVar1 = SearchInstanceCell(this,param_1);
  if (iVar1 != 0) {
    while (p_Var2 = (_utlCell *)UtilList::GetTopCellFromList((_utlList *)(iVar1 + 0xc)),
          p_Var2 != (_utlCell *)0x0) {
      UtilList::RemoveCellFromList((_utlList *)(iVar1 + 0xc),p_Var2);
      if (*(void **)(p_Var2 + 0xc) != (void *)0x0) {
        operator_delete__(*(void **)(p_Var2 + 0xc));
      }
      operator_delete(p_Var2);
    }
  }
  (*(code *)PTR_Unlock_0004c134)(*(undefined4 *)(this + 0x10));
  return;
}


/* 0002c792 */

/* EventSwitcher::AddCallbackFunc(void*, unsigned int, EventSwitcher::_CallbackEntry*) */

void __thiscall
EventSwitcher::AddCallbackFunc
          (EventSwitcher *this,void *param_1,uint param_2,_CallbackEntry *param_3)

{
  int iVar1;
  _utlCell *p_Var2;
  void *pvVar3;
  
  MWF::ObjLock::Lock(*(ObjLock **)(this + 0x10));
  iVar1 = SearchInstanceCell(this,param_1);
  if ((iVar1 != 0) && (p_Var2 = operator_new(0x10), p_Var2 != (_utlCell *)0x0)) {
    MemUtil::MemSet8(p_Var2,'\0',0x10);
    pvVar3 = operator_new__(param_2 << 4);
    *(void **)(p_Var2 + 0xc) = pvVar3;
    if (pvVar3 == (void *)0x0) {
      operator_delete(p_Var2);
    }
    else {
      *(uint *)(p_Var2 + 8) = param_2;
      MemUtil::MemCpy8(pvVar3,param_3,param_2 << 4);
      UtilList::AddCellToList((_utlList *)(iVar1 + 0xc),p_Var2);
    }
  }
  (*(code *)PTR_Unlock_0004c134)(*(undefined4 *)(this + 0x10));
  return;
}


/* 0002c7f8 */

/* EventSwitcher::DeleteInstance(void*) */

void __thiscall EventSwitcher::DeleteInstance(EventSwitcher *this,void *param_1)

{
  _utlCell *p_Var1;
  
  MWF::ObjLock::Lock(*(ObjLock **)(this + 0x10));
  p_Var1 = (_utlCell *)SearchInstanceCell(this,param_1);
  if (p_Var1 != (_utlCell *)0x0) {
    UtilList::RemoveCellFromList((_utlList *)(this + 4),p_Var1);
    operator_delete(p_Var1);
  }
  (*(code *)PTR_Unlock_0004c134)(*(undefined4 *)(this + 0x10));
  return;
}


/* 0002c82a */

/* EventSwitcher::AddInstance(void*) */

void __thiscall EventSwitcher::AddInstance(EventSwitcher *this,void *param_1)

{
  int iVar1;
  _utlCell *p_Var2;
  
  MWF::ObjLock::Lock(*(ObjLock **)(this + 0x10));
  iVar1 = SearchInstanceCell(this,param_1);
  if ((iVar1 == 0) && (p_Var2 = operator_new(0x18), p_Var2 != (_utlCell *)0x0)) {
    MemUtil::MemSet8(p_Var2,'\0',0x18);
    *(void **)(p_Var2 + 8) = param_1;
    UtilList::AddCellToList((_utlList *)(this + 4),p_Var2);
  }
  (*(code *)PTR_Unlock_0004c134)(*(undefined4 *)(this + 0x10));
  return;
}


/* 0002c86c */

/* EventSwitcher::Callback(EventSwitcher::_CallbackEntry*, unsigned int, void*, unsigned int) */

void __thiscall
EventSwitcher::Callback
          (EventSwitcher *this,_CallbackEntry *param_1,uint param_2,void *param_3,uint param_4)

{
  (**(code **)(param_1 + 8))
            (*(undefined4 *)param_1,param_2,param_3,param_4,*(undefined4 *)(param_1 + 0xc));
  return;
}


/* 0002c88a */

/* EventSwitcher::CallbackPoint(unsigned long, unsigned long, void*, unsigned long, void*) */

void EventSwitcher::CallbackPoint
               (ulong param_1,ulong param_2,void *param_3,ulong param_4,void *param_5)

{
  _utlCell *p_Var1;
  _utlCell *p_Var2;
  _CallbackEntry *p_Var3;
  ulong uVar4;
  uint uVar5;
  
  MWF::ObjLock::Lock(*(ObjLock **)((int)param_5 + 0x10));
  for (p_Var1 = (_utlCell *)UtilList::GetTopCellFromList((_utlList *)((int)param_5 + 4));
      p_Var1 != (_utlCell *)0x0; p_Var1 = (_utlCell *)UtilList::GetNextCell(p_Var1)) {
    for (p_Var2 = (_utlCell *)UtilList::GetTopCellFromList((_utlList *)(p_Var1 + 0xc));
        p_Var2 != (_utlCell *)0x0; p_Var2 = (_utlCell *)UtilList::GetNextCell(p_Var2)) {
      for (uVar5 = 0; uVar5 < *(uint *)(p_Var2 + 8); uVar5 = uVar5 + 1) {
        p_Var3 = (_CallbackEntry *)(*(int *)(p_Var2 + 0xc) + uVar5 * 0x10);
        if ((*(ulong *)(p_Var3 + 4) == param_2) &&
           ((uVar4 = *(ulong *)(*(int *)(p_Var2 + 0xc) + uVar5 * 0x10), uVar4 == 0 ||
            (uVar4 == param_1)))) {
          Callback(param_5,p_Var3,param_2,param_3,param_4);
        }
      }
    }
  }
  (*(code *)PTR_Unlock_0004c134)(*(undefined4 *)((int)param_5 + 0x10));
  return;
}


/* 0002c910 */

/* StatMgr::~StatMgr() */

StatMgr * __thiscall StatMgr::~StatMgr(StatMgr *this)

{
  _utlCell *p_Var1;
  
  *(int *)this = *(int *)(DAT_0002c96c + 0x2c920 + DAT_0002c970) + 8;
  while (p_Var1 = (_utlCell *)UtilList::GetTopCellFromList((_utlList *)(this + 0xc)),
        p_Var1 != (_utlCell *)0x0) {
    UtilList::RemoveCellFromList((_utlList *)(this + 0xc),p_Var1);
    if (*(void **)(p_Var1 + 0xc) != (void *)0x0) {
      operator_delete__(*(void **)(p_Var1 + 0xc));
    }
    operator_delete(p_Var1);
  }
  if (*(int **)(this + 0x18) != (int *)0x0) {
    (**(code **)(**(int **)(this + 0x18) + 4))();
  }
  if (*(int **)(this + 0x1c) != (int *)0x0) {
    (**(code **)(**(int **)(this + 0x1c) + 4))();
  }
  if (*(int **)(this + 0x28) != (int *)0x0) {
    (**(code **)(**(int **)(this + 0x28) + 4))();
  }
  return this;
}


/* 0002c974 */

/* StatMgr::~StatMgr() */

StatMgr * __thiscall StatMgr::~StatMgr(StatMgr *this)

{
  ~StatMgr(this);
  operator_delete(this);
  return this;
}


/* 0002c988 */

/* StrUtil::StrLen(char const*) */

void StrUtil::StrLen(char *param_1)

{
  (*(code *)PTR_strlen_0004bf34)(param_1);
  return;
}


/* 0002c994 */

/* StrUtil::StrNCat(char*, char const*, int) */

void StrUtil::StrNCat(char *param_1,char *param_2,int param_3)

{
  (*(code *)PTR_strncat_0004bfdc)(param_1);
  return;
}


/* 0002c9a0 */

/* StrUtil::StrNCpy(char*, char const*, int) */

void StrUtil::StrNCpy(char *param_1,char *param_2,int param_3)

{
  (*(code *)PTR_strncpy_0004bd90)(param_1);
  return;
}


/* 0002c9ac */

/* StatMgr::StatMgr(char*, void*, unsigned int, bool) */

StatMgr * __thiscall
StatMgr::StatMgr(StatMgr *this,char *param_1,void *param_2,uint param_3,bool param_4)

{
  int iVar1;
  int iVar2;
  MonCtrl *this_00;
  ObjLock *pOVar3;
  StatMgr *pSVar4;
  char *pcVar5;
  
  pcVar5 = (char *)(DAT_0002ca80 + 0x2c9d0);
  pSVar4 = this + 0x2c;
  *(int *)this = *(int *)(DAT_0002ca78 + 0x2c9c0 + DAT_0002ca7c) + 8;
  MemUtil::MemSet8(pSVar4,'\0',0x21);
  iVar1 = StrUtil::StrLen(pcVar5);
  StrUtil::StrNCpy((char *)pSVar4,pcVar5,iVar1);
  iVar1 = StrUtil::StrLen((char *)pSVar4);
  iVar2 = StrUtil::StrLen(param_1);
  if (0x20 < iVar1 + iVar2) {
    param_1 = (char *)(DAT_0002ca84 + 0x2ca10);
    iVar2 = StrUtil::StrLen(param_1);
  }
  StrUtil::StrNCat((char *)pSVar4,param_1,iVar2);
  this_00 = operator_new(0xc);
  MonCtrl::MonCtrl(this_00,(char *)pSVar4,true);
  *(MonCtrl **)(this + 0x28) = this_00;
  pOVar3 = operator_new(0x1c);
  MWF::ObjLock::ObjLock(pOVar3);
  *(ObjLock **)(this + 0x18) = pOVar3;
  pOVar3 = operator_new(0x1c);
  MWF::ObjLock::ObjLock(pOVar3);
  *(ObjLock **)(this + 0x1c) = pOVar3;
  *(void **)(this + 4) = param_2;
  *(uint *)(this + 8) = param_3;
  this[0x24] = (StatMgr)param_4;
  *(undefined4 *)(this + 0x20) = 0;
  MemUtil::MemSet8(this + 0xc,'\0',0xc);
  return this;
}


/* 0002ca88 */

/* StatMgr::AddEntry(unsigned int, StatMgr::_FuncEntry*) */

int __thiscall StatMgr::AddEntry(StatMgr *this,uint param_1,_FuncEntry *param_2)

{
  _utlCell *p_Var1;
  void *__dest;
  int iVar2;
  
  MWF::ObjLock::Lock(*(ObjLock **)(this + 0x1c));
  p_Var1 = operator_new(0x10);
  iVar2 = 0;
  if (p_Var1 != (_utlCell *)0x0) {
    MemUtil::MemSet8(p_Var1,'\0',0x10);
    __dest = operator_new__(param_1 * 0x1c);
    *(void **)(p_Var1 + 0xc) = __dest;
    if (__dest == (void *)0x0) {
      operator_delete(p_Var1);
      iVar2 = 0;
    }
    else {
      *(uint *)(p_Var1 + 8) = param_1;
      memcpy(__dest,param_2,param_1 * 0x1c);
      iVar2 = 1;
      UtilList::AddCellToList((_utlList *)(this + 0xc),p_Var1);
    }
  }
  MWF::ObjLock::Unlock(*(ObjLock **)(this + 0x1c));
  if (iVar2 == 0) {
    MonCtrl::ConPrintfMessage(*(char **)(this + 0x28),DAT_0002caf8 + 0x2caf0);
  }
  return iVar2;
}


/* 0002cafc */

/* StatMgr::DelAllEntry() */

undefined4 __thiscall StatMgr::DelAllEntry(StatMgr *this)

{
  _utlCell *p_Var1;
  
  MWF::ObjLock::Lock(*(ObjLock **)(this + 0x1c));
  while (p_Var1 = (_utlCell *)UtilList::GetTopCellFromList((_utlList *)(this + 0xc)),
        p_Var1 != (_utlCell *)0x0) {
    UtilList::RemoveCellFromList((_utlList *)(this + 0xc),p_Var1);
    if (*(void **)(p_Var1 + 0xc) != (void *)0x0) {
      operator_delete__(*(void **)(p_Var1 + 0xc));
    }
    operator_delete(p_Var1);
  }
  MWF::ObjLock::Unlock(*(ObjLock **)(this + 0x1c));
  return 1;
}


/* 0002cb3a */

/* StatMgr::GetCurrentState() */

undefined4 __thiscall StatMgr::GetCurrentState(StatMgr *this)

{
  undefined4 uVar1;
  
  MWF::ObjLock::Lock(*(ObjLock **)(this + 0x18));
  uVar1 = *(undefined4 *)(this + 8);
  MWF::ObjLock::Unlock(*(ObjLock **)(this + 0x18));
  return uVar1;
}


/* 0002cb52 */

/* StatMgr::UpdateCurrentState(unsigned int) */

void __thiscall StatMgr::UpdateCurrentState(StatMgr *this,uint param_1)

{
  MWF::ObjLock::Lock(*(ObjLock **)(this + 0x18));
  *(uint *)(this + 8) = param_1;
  (*(code *)PTR_Unlock_0004c134)(*(undefined4 *)(this + 0x18));
  return;
}


/* 0002cb6c */

/* StatMgr::CheckFunc(StatMgr::_FuncEntry*, void*, unsigned int) */

void __thiscall StatMgr::CheckFunc(StatMgr *this,_FuncEntry *param_1,void *param_2,uint param_3)

{
  (**(code **)(param_1 + 0xc))(*(undefined4 *)(this + 8),param_2,param_3,*(undefined4 *)(this + 4));
  return;
}


/* 0002cb80 */

/* StatMgr::CallFunc(StatMgr::_FuncEntry*, void*, unsigned int) */

void __thiscall StatMgr::CallFunc(StatMgr *this,_FuncEntry *param_1,void *param_2,uint param_3)

{
  (**(code **)(param_1 + 0x10))(param_2,param_3,*(undefined4 *)(this + 4));
  return;
}


/* 0002cb92 */

/* StatMgr::GetNextState(StatMgr::_FuncEntry*, int) */

void StatMgr::GetNextState(_FuncEntry *param_1,int param_2)

{
  undefined4 in_r2;
  
  (**(code **)(param_2 + 0x14))
            (*(undefined4 *)(param_1 + 8),*(undefined4 *)(param_2 + 0x18),in_r2,
             *(undefined4 *)(param_1 + 4));
  return;
}


/* 0002cba4 */

/* StatMgr::ChangeState(unsigned int, unsigned int, void*, unsigned int) */

int __thiscall
StatMgr::ChangeState(StatMgr *this,uint param_1,uint param_2,void *param_3,uint param_4)

{
  _utlCell *p_Var1;
  uint uVar2;
  _FuncEntry *p_Var3;
  int iVar4;
  
  if (*(int *)(this + 0x20) != 0) {
    MonCtrl::ConPrintfMessage(*(char **)(this + 0x28),DAT_0002cc94 + 0x2cbc0);
  }
  MWF::ObjLock::Lock(*(ObjLock **)(this + 0x1c));
  *(int *)(this + 0x20) = *(int *)(this + 0x20) + 1;
  for (p_Var1 = (_utlCell *)UtilList::GetTopCellFromList((_utlList *)(this + 0xc));
      p_Var1 != (_utlCell *)0x0; p_Var1 = (_utlCell *)UtilList::GetNextCell(p_Var1)) {
    iVar4 = 0;
    for (uVar2 = 0; uVar2 < *(uint *)(p_Var1 + 8); uVar2 = uVar2 + 1) {
      p_Var3 = (_FuncEntry *)(*(int *)(p_Var1 + 0xc) + uVar2 * 0x1c);
      if (((*(int *)(*(int *)(p_Var1 + 0xc) + uVar2 * 0x1c) == *(int *)(this + 8)) &&
          (*(uint *)(p_Var3 + 4) == param_1)) &&
         ((*(uint *)(p_Var3 + 8) == 0xffffffff || (*(uint *)(p_Var3 + 8) == param_2)))) {
        if ((*(int *)(p_Var3 + 0xc) == 0) ||
           (iVar4 = CheckFunc(this,p_Var3,param_3,param_4), iVar4 != 0)) {
          if (*(int *)(p_Var3 + 0x10) != 0) {
            CallFunc(this,p_Var3,param_3,param_4);
          }
          if (*(int *)(p_Var3 + 0x14) == 0) {
            uVar2 = *(uint *)(p_Var3 + 0x18);
          }
          else {
            uVar2 = GetNextState((_FuncEntry *)this,(int)p_Var3);
          }
          iVar4 = 1;
          UpdateCurrentState(this,uVar2);
          goto LAB_0002cc68;
        }
        iVar4 = 1;
      }
    }
    if (iVar4 != 0) goto LAB_0002cc68;
  }
  iVar4 = 0;
LAB_0002cc68:
  *(int *)(this + 0x20) = *(int *)(this + 0x20) + -1;
  MWF::ObjLock::Unlock(*(ObjLock **)(this + 0x1c));
  if (iVar4 == 0) {
    MonCtrl::ConPrintfMessage
              (*(char **)(this + 0x28),DAT_0002cc98 + 0x2cc84,*(undefined4 *)(this + 8),param_1);
  }
  return iVar4;
}


/* 0002cc9c */

/* StateMgr::~StateMgr() */

StateMgr * __thiscall StateMgr::~StateMgr(StateMgr *this)

{
  _utlCell *p_Var1;
  
  *(int *)this = *(int *)(DAT_0002ccf8 + 0x2ccac + DAT_0002ccfc) + 8;
  while (p_Var1 = (_utlCell *)UtilList::GetTopCellFromList((_utlList *)(this + 0xc)),
        p_Var1 != (_utlCell *)0x0) {
    UtilList::RemoveCellFromList((_utlList *)(this + 0xc),p_Var1);
    if (*(void **)(p_Var1 + 0xc) != (void *)0x0) {
      operator_delete__(*(void **)(p_Var1 + 0xc));
    }
    operator_delete(p_Var1);
  }
  if (*(int **)(this + 0x18) != (int *)0x0) {
    (**(code **)(**(int **)(this + 0x18) + 4))();
  }
  if (*(int **)(this + 0x1c) != (int *)0x0) {
    (**(code **)(**(int **)(this + 0x1c) + 4))();
  }
  if (*(int **)(this + 0x28) != (int *)0x0) {
    (**(code **)(**(int **)(this + 0x28) + 4))();
  }
  return this;
}


/* 0002cd00 */

/* StateMgr::~StateMgr() */

StateMgr * __thiscall StateMgr::~StateMgr(StateMgr *this)

{
  ~StateMgr(this);
  operator_delete(this);
  return this;
}


/* 0002cd14 */

/* StateMgr::StateMgr(char*, void*, unsigned int, bool) */

StateMgr * __thiscall
StateMgr::StateMgr(StateMgr *this,char *param_1,void *param_2,uint param_3,bool param_4)

{
  int iVar1;
  int iVar2;
  MonCtrl *this_00;
  ObjLock *pOVar3;
  StateMgr *pSVar4;
  char *pcVar5;
  
  pcVar5 = (char *)(DAT_0002cde8 + 0x2cd38);
  pSVar4 = this + 0x2c;
  *(int *)this = *(int *)(DAT_0002cde0 + 0x2cd28 + DAT_0002cde4) + 8;
  MemUtil::MemSet8(pSVar4,'\0',0x21);
  iVar1 = StrUtil::StrLen(pcVar5);
  StrUtil::StrNCpy((char *)pSVar4,pcVar5,iVar1);
  iVar1 = StrUtil::StrLen((char *)pSVar4);
  iVar2 = StrUtil::StrLen(param_1);
  if (0x20 < iVar1 + iVar2) {
    param_1 = (char *)(DAT_0002cdec + 0x2cd78);
    iVar2 = StrUtil::StrLen(param_1);
  }
  StrUtil::StrNCat((char *)pSVar4,param_1,iVar2);
  this_00 = operator_new(0xc);
  MonCtrl::MonCtrl(this_00,(char *)pSVar4,true);
  *(MonCtrl **)(this + 0x28) = this_00;
  pOVar3 = operator_new(0x1c);
  MWF::ObjLock::ObjLock(pOVar3);
  *(ObjLock **)(this + 0x18) = pOVar3;
  pOVar3 = operator_new(0x1c);
  MWF::ObjLock::ObjLock(pOVar3);
  *(ObjLock **)(this + 0x1c) = pOVar3;
  *(void **)(this + 4) = param_2;
  *(uint *)(this + 8) = param_3;
  this[0x24] = (StateMgr)param_4;
  *(undefined4 *)(this + 0x20) = 0;
  MemUtil::MemSet8(this + 0xc,'\0',0xc);
  return this;
}


/* 0002cdf0 */

/* StateMgr::AddEntry(unsigned int, StateMgr::_FuncEntry*) */

int __thiscall StateMgr::AddEntry(StateMgr *this,uint param_1,_FuncEntry *param_2)

{
  _utlCell *p_Var1;
  void *pvVar2;
  int iVar3;
  
  MWF::ObjLock::Lock(*(ObjLock **)(this + 0x1c));
  p_Var1 = operator_new(0x10);
  iVar3 = 0;
  if (p_Var1 != (_utlCell *)0x0) {
    MemUtil::MemSet8(p_Var1,'\0',0x10);
    pvVar2 = operator_new__(param_1 * 0x18);
    *(void **)(p_Var1 + 0xc) = pvVar2;
    if (pvVar2 == (void *)0x0) {
      operator_delete(p_Var1);
      iVar3 = 0;
    }
    else {
      *(uint *)(p_Var1 + 8) = param_1;
      MemUtil::MemCpy8(pvVar2,param_2,param_1 * 0x18);
      iVar3 = 1;
      UtilList::AddCellToList((_utlList *)(this + 0xc),p_Var1);
    }
  }
  MWF::ObjLock::Unlock(*(ObjLock **)(this + 0x1c));
  if (iVar3 == 0) {
    MonCtrl::ConPrintfMessage(*(char **)(this + 0x28),DAT_0002ce60 + 0x2ce58);
  }
  return iVar3;
}


/* 0002ce64 */

/* StateMgr::DelAllEntry() */

undefined4 __thiscall StateMgr::DelAllEntry(StateMgr *this)

{
  _utlCell *p_Var1;
  
  MWF::ObjLock::Lock(*(ObjLock **)(this + 0x1c));
  while (p_Var1 = (_utlCell *)UtilList::GetTopCellFromList((_utlList *)(this + 0xc)),
        p_Var1 != (_utlCell *)0x0) {
    UtilList::RemoveCellFromList((_utlList *)(this + 0xc),p_Var1);
    if (*(void **)(p_Var1 + 0xc) != (void *)0x0) {
      operator_delete__(*(void **)(p_Var1 + 0xc));
    }
    operator_delete(p_Var1);
  }
  MWF::ObjLock::Unlock(*(ObjLock **)(this + 0x1c));
  return 1;
}


/* 0002cea2 */

/* StateMgr::GetCurrentState() */

undefined4 __thiscall StateMgr::GetCurrentState(StateMgr *this)

{
  undefined4 uVar1;
  
  MWF::ObjLock::Lock(*(ObjLock **)(this + 0x18));
  uVar1 = *(undefined4 *)(this + 8);
  MWF::ObjLock::Unlock(*(ObjLock **)(this + 0x18));
  return uVar1;
}


/* 0002ceba */

/* StateMgr::UpdateCurrentState(unsigned int) */

void __thiscall StateMgr::UpdateCurrentState(StateMgr *this,uint param_1)

{
  MWF::ObjLock::Lock(*(ObjLock **)(this + 0x18));
  *(uint *)(this + 8) = param_1;
  (*(code *)PTR_Unlock_0004c134)(*(undefined4 *)(this + 0x18));
  return;
}


/* 0002ced4 */

/* StateMgr::CheckFunc(StateMgr::_FuncEntry*, MWF::ObjMsg*) */

void StateMgr::CheckFunc(_FuncEntry *param_1,ObjMsg *param_2)

{
  (**(code **)(param_2 + 8))();
  return;
}


/* 0002cee6 */

/* StateMgr::CallFunc(StateMgr::_FuncEntry*, MWF::ObjMsg*) */

void StateMgr::CallFunc(_FuncEntry *param_1,ObjMsg *param_2)

{
  (**(code **)(param_2 + 0xc))();
  return;
}


/* 0002cef6 */

/* StateMgr::GetNextState(StateMgr::_FuncEntry*, MWF::ObjMsg*, int) */

void __thiscall
StateMgr::GetNextState(StateMgr *this,_FuncEntry *param_1,ObjMsg *param_2,int param_3)

{
  (**(code **)(param_1 + 0x10))
            (param_2,*(undefined4 *)(this + 8),*(undefined4 *)(param_1 + 0x14),param_3,
             *(undefined4 *)(this + 4));
  return;
}


/* 0002cf18 */

/* StateMgr::ChangeState(unsigned int, MWF::ObjMsg*) */

uint __thiscall StateMgr::ChangeState(StateMgr *this,uint param_1,ObjMsg *param_2)

{
  _utlCell *p_Var1;
  int iVar2;
  int iVar3;
  uint uVar4;
  _FuncEntry *p_Var5;
  uint uVar6;
  
  if (*(int *)(this + 0x20) != 0) {
    MonCtrl::ConPrintfMessage(*(char **)(this + 0x28),DAT_0002cff4 + 0x2cf32);
  }
  MWF::ObjLock::Lock(*(ObjLock **)(this + 0x1c));
  *(int *)(this + 0x20) = *(int *)(this + 0x20) + 1;
  for (p_Var1 = (_utlCell *)UtilList::GetTopCellFromList((_utlList *)(this + 0xc));
      p_Var1 != (_utlCell *)0x0; p_Var1 = (_utlCell *)UtilList::GetNextCell(p_Var1)) {
    iVar3 = 0;
    uVar6 = 0;
    for (uVar4 = uVar6; uVar4 < *(uint *)(p_Var1 + 8); uVar4 = uVar4 + 1) {
      p_Var5 = (_FuncEntry *)(*(int *)(p_Var1 + 0xc) + iVar3);
      if ((*(int *)(*(int *)(p_Var1 + 0xc) + iVar3) == *(int *)(this + 8)) &&
         (*(uint *)(p_Var5 + 4) == param_1)) {
        if ((*(int *)(p_Var5 + 8) == 0) ||
           (iVar2 = CheckFunc((_FuncEntry *)this,p_Var5), iVar2 != 0)) {
          iVar3 = 0;
          if (*(int *)(p_Var5 + 0xc) != 0) {
            iVar3 = CallFunc((_FuncEntry *)this,p_Var5);
          }
          if (*(int *)(p_Var5 + 0x10) == 0) {
            uVar4 = *(uint *)(p_Var5 + 0x14);
          }
          else {
            uVar4 = GetNextState(this,p_Var5,param_2,iVar3);
          }
          uVar6 = 1;
          UpdateCurrentState(this,uVar4);
          goto LAB_0002cfcc;
        }
        uVar6 = 1;
      }
      iVar3 = iVar3 + 0x18;
    }
    if (uVar6 != 0) goto LAB_0002cfcc;
  }
  uVar6 = 0;
LAB_0002cfcc:
  *(int *)(this + 0x20) = *(int *)(this + 0x20) + -1;
  MWF::ObjLock::Unlock(*(ObjLock **)(this + 0x1c));
  if (uVar6 == 0) {
    MonCtrl::ConPrintfMessage
              (*(char **)(this + 0x28),DAT_0002cff8 + 0x2cfe2,*(undefined4 *)(this + 8),param_1);
  }
  return uVar6;
}


/* 0002cffc */

/* MprCnv::Exchg_LocalTime(MPR::T_LTM*, DefStruct::LocalTime*) */

void MprCnv::Exchg_LocalTime(T_LTM *param_1,LocalTime *param_2)

{
  *(undefined2 *)param_1 = *(undefined2 *)param_2;
  *(undefined2 *)(param_1 + 2) = *(undefined2 *)(param_2 + 2);
  param_1[4] = *(T_LTM *)(param_2 + 4);
  param_1[5] = *(T_LTM *)(param_2 + 5);
  param_1[6] = *(T_LTM *)(param_2 + 6);
  param_1[7] = *(T_LTM *)(param_2 + 7);
  param_1[8] = *(T_LTM *)(param_2 + 8);
  return;
}


/* 0002d01e */

/* MprCnv::Exchg_LocalTime(DefStruct::LocalTime*, MPR::T_LTM*) */

void MprCnv::Exchg_LocalTime(LocalTime *param_1,T_LTM *param_2)

{
  *(undefined2 *)param_1 = *(undefined2 *)param_2;
  *(undefined2 *)(param_1 + 2) = *(undefined2 *)(param_2 + 2);
  param_1[4] = *(LocalTime *)(param_2 + 4);
  param_1[5] = *(LocalTime *)(param_2 + 5);
  param_1[6] = *(LocalTime *)(param_2 + 6);
  param_1[7] = *(LocalTime *)(param_2 + 7);
  param_1[8] = *(LocalTime *)(param_2 + 8);
  return;
}


/* 0002d040 */

/* MprCnv::Exchg_CamInfo(MPR::CamInfo*, DefStruct::CamInfo*) */

void MprCnv::Exchg_CamInfo(CamInfo *param_1,CamInfo *param_2)

{
  *param_1 = *(CamInfo *)param_2;
  *(undefined4 *)(param_1 + 4) = *(undefined4 *)(param_2 + 4);
  *(undefined4 *)(param_1 + 8) = *(undefined4 *)(param_2 + 8);
  param_1[0xc] = *(CamInfo *)(param_2 + 0xc);
  *(undefined4 *)(param_1 + 0x10) = *(undefined4 *)(param_2 + 0x10);
  *(undefined4 *)(param_1 + 0x14) = *(undefined4 *)(param_2 + 0x14);
  param_1[0x18] = *(CamInfo *)(param_2 + 0x18);
  *(undefined2 *)(param_1 + 0x1a) = *(undefined2 *)(param_2 + 0x1a);
  param_1[0x1c] = *(CamInfo *)(param_2 + 0x1c);
  *(undefined4 *)(param_1 + 0x20) = *(undefined4 *)(param_2 + 0x20);
  *(undefined4 *)(param_1 + 0x24) = *(undefined4 *)(param_2 + 0x24);
  param_1[0x28] = *(CamInfo *)(param_2 + 0x28);
  *(undefined4 *)(param_1 + 0x2c) = *(undefined4 *)(param_2 + 0x2c);
  *(undefined4 *)(param_1 + 0x30) = *(undefined4 *)(param_2 + 0x30);
  param_1[0x34] = *(CamInfo *)(param_2 + 0x34);
  *(undefined4 *)(param_1 + 0x38) = *(undefined4 *)(param_2 + 0x38);
  *(undefined4 *)(param_1 + 0x3c) = *(undefined4 *)(param_2 + 0x3c);
  param_1[0x40] = *(CamInfo *)(param_2 + 0x40);
  *(undefined2 *)(param_1 + 0x42) = *(undefined2 *)(param_2 + 0x42);
  param_1[0x44] = *(CamInfo *)(param_2 + 0x44);
  *(undefined2 *)(param_1 + 0x46) = *(undefined2 *)(param_2 + 0x46);
  param_1[0x48] = *(CamInfo *)(param_2 + 0x48);
  *(undefined2 *)(param_1 + 0x4a) = *(undefined2 *)(param_2 + 0x4a);
  param_1[0x4c] = *(CamInfo *)(param_2 + 0x4c);
  *(undefined2 *)(param_1 + 0x4e) = *(undefined2 *)(param_2 + 0x4e);
  param_1[0x50] = *(CamInfo *)(param_2 + 0x50);
  *(undefined4 *)(param_1 + 0x54) = *(undefined4 *)(param_2 + 0x54);
  *(undefined4 *)(param_1 + 0x58) = *(undefined4 *)(param_2 + 0x58);
  param_1[0x5c] = *(CamInfo *)(param_2 + 0x5c);
  *(undefined4 *)(param_1 + 0x60) = *(undefined4 *)(param_2 + 0x60);
  *(undefined4 *)(param_1 + 100) = *(undefined4 *)(param_2 + 100);
  param_1[0x68] = *(CamInfo *)(param_2 + 0x68);
  *(undefined2 *)(param_1 + 0x6a) = *(undefined2 *)(param_2 + 0x6a);
  param_1[0x6c] = *(CamInfo *)(param_2 + 0x6c);
  param_1[0x6d] = *(CamInfo *)(param_2 + 0x6d);
  param_1[0x6e] = *(CamInfo *)(param_2 + 0x6e);
  param_1[0x6f] = *(CamInfo *)(param_2 + 0x6f);
  param_1[0x70] = *(CamInfo *)(param_2 + 0x70);
  param_1[0x71] = *(CamInfo *)(param_2 + 0x71);
  param_1[0x72] = *(CamInfo *)(param_2 + 0x72);
  *(undefined2 *)(param_1 + 0x74) = *(undefined2 *)(param_2 + 0x74);
  param_1[0x76] = *(CamInfo *)(param_2 + 0x76);
  *(undefined2 *)(param_1 + 0x78) = *(undefined2 *)(param_2 + 0x78);
  param_1[0x7a] = *(CamInfo *)(param_2 + 0x7a);
  *(undefined2 *)(param_1 + 0x7c) = *(undefined2 *)(param_2 + 0x7c);
  param_1[0xe8] = *(CamInfo *)(param_2 + 0x7e);
  *(undefined4 *)(param_1 + 0xec) = *(undefined4 *)(param_2 + 0x80);
  param_1[0xf0] = *(CamInfo *)(param_2 + 0x84);
  param_1[0x7e] = (CamInfo)0x0;
  param_1[0x84] = (CamInfo)0x0;
  param_1[0x8c] = (CamInfo)0x0;
  param_1[0x94] = (CamInfo)0x0;
  param_1[0x9c] = (CamInfo)0x0;
  param_1[0xa4] = (CamInfo)0x0;
  param_1[0xa8] = (CamInfo)0x0;
  param_1[0xb4] = (CamInfo)0x0;
  param_1[0xbc] = (CamInfo)0x0;
  param_1[0xc4] = (CamInfo)0x0;
  param_1[0xcc] = (CamInfo)0x0;
  param_1[0xd4] = (CamInfo)0x0;
  param_1[0xe0] = (CamInfo)0x0;
  param_1[0xe4] = (CamInfo)0x0;
  param_1[0xf1] = (CamInfo)0x0;
  param_1[0xf4] = (CamInfo)0x0;
  return;
}


/* 0002d1bc */

/* MprCnv::Exchg_CamInfo(DefStruct::CamInfo*, MPR::CamInfo*) */

void MprCnv::Exchg_CamInfo(CamInfo *param_1,CamInfo *param_2)

{
  *param_1 = *(CamInfo *)param_2;
  *(undefined4 *)(param_1 + 4) = *(undefined4 *)(param_2 + 4);
  *(undefined4 *)(param_1 + 8) = *(undefined4 *)(param_2 + 8);
  param_1[0xc] = *(CamInfo *)(param_2 + 0xc);
  *(undefined4 *)(param_1 + 0x10) = *(undefined4 *)(param_2 + 0x10);
  *(undefined4 *)(param_1 + 0x14) = *(undefined4 *)(param_2 + 0x14);
  param_1[0x18] = *(CamInfo *)(param_2 + 0x18);
  *(undefined2 *)(param_1 + 0x1a) = *(undefined2 *)(param_2 + 0x1a);
  param_1[0x1c] = *(CamInfo *)(param_2 + 0x1c);
  *(undefined4 *)(param_1 + 0x20) = *(undefined4 *)(param_2 + 0x20);
  *(undefined4 *)(param_1 + 0x24) = *(undefined4 *)(param_2 + 0x24);
  param_1[0x28] = *(CamInfo *)(param_2 + 0x28);
  *(undefined4 *)(param_1 + 0x2c) = *(undefined4 *)(param_2 + 0x2c);
  *(undefined4 *)(param_1 + 0x30) = *(undefined4 *)(param_2 + 0x30);
  param_1[0x34] = *(CamInfo *)(param_2 + 0x34);
  *(undefined4 *)(param_1 + 0x38) = *(undefined4 *)(param_2 + 0x38);
  *(undefined4 *)(param_1 + 0x3c) = *(undefined4 *)(param_2 + 0x3c);
  param_1[0x40] = *(CamInfo *)(param_2 + 0x40);
  *(undefined2 *)(param_1 + 0x42) = *(undefined2 *)(param_2 + 0x42);
  param_1[0x44] = *(CamInfo *)(param_2 + 0x44);
  *(undefined2 *)(param_1 + 0x46) = *(undefined2 *)(param_2 + 0x46);
  param_1[0x48] = *(CamInfo *)(param_2 + 0x48);
  *(undefined2 *)(param_1 + 0x4a) = *(undefined2 *)(param_2 + 0x4a);
  param_1[0x4c] = *(CamInfo *)(param_2 + 0x4c);
  *(undefined2 *)(param_1 + 0x4e) = *(undefined2 *)(param_2 + 0x4e);
  param_1[0x50] = *(CamInfo *)(param_2 + 0x50);
  *(undefined4 *)(param_1 + 0x54) = *(undefined4 *)(param_2 + 0x54);
  *(undefined4 *)(param_1 + 0x58) = *(undefined4 *)(param_2 + 0x58);
  param_1[0x5c] = *(CamInfo *)(param_2 + 0x5c);
  *(undefined4 *)(param_1 + 0x60) = *(undefined4 *)(param_2 + 0x60);
  *(undefined4 *)(param_1 + 100) = *(undefined4 *)(param_2 + 100);
  param_1[0x68] = *(CamInfo *)(param_2 + 0x68);
  *(undefined2 *)(param_1 + 0x6a) = *(undefined2 *)(param_2 + 0x6a);
  param_1[0x6c] = *(CamInfo *)(param_2 + 0x6c);
  param_1[0x6d] = *(CamInfo *)(param_2 + 0x6d);
  param_1[0x6e] = *(CamInfo *)(param_2 + 0x6e);
  param_1[0x6f] = *(CamInfo *)(param_2 + 0x6f);
  param_1[0x70] = *(CamInfo *)(param_2 + 0x70);
  param_1[0x71] = *(CamInfo *)(param_2 + 0x71);
  param_1[0x72] = *(CamInfo *)(param_2 + 0x72);
  *(undefined2 *)(param_1 + 0x74) = *(undefined2 *)(param_2 + 0x74);
  param_1[0x76] = *(CamInfo *)(param_2 + 0x76);
  *(undefined2 *)(param_1 + 0x78) = *(undefined2 *)(param_2 + 0x78);
  param_1[0x7a] = *(CamInfo *)(param_2 + 0x7a);
  *(undefined2 *)(param_1 + 0x7c) = *(undefined2 *)(param_2 + 0x7c);
  param_1[0x7e] = *(CamInfo *)(param_2 + 0xe8);
  *(undefined4 *)(param_1 + 0x80) = *(undefined4 *)(param_2 + 0xec);
  param_1[0x84] = *(CamInfo *)(param_2 + 0xf0);
  return;
}


/* 0002d2f6 */

/* MprCnv::Exchg_ExtCamInfo(DefStruct::ExtCamInfo*, MPR::CamInfo*) */

void MprCnv::Exchg_ExtCamInfo(ExtCamInfo *param_1,CamInfo *param_2)

{
  *param_1 = *(ExtCamInfo *)(param_2 + 0x7e);
  *(undefined4 *)(param_1 + 4) = *(undefined4 *)(param_2 + 0x80);
  param_1[8] = *(ExtCamInfo *)(param_2 + 0x84);
  *(undefined4 *)(param_1 + 0xc) = *(undefined4 *)(param_2 + 0x88);
  param_1[0x10] = *(ExtCamInfo *)(param_2 + 0x8c);
  *(undefined4 *)(param_1 + 0x14) = *(undefined4 *)(param_2 + 0x90);
  param_1[0x18] = *(ExtCamInfo *)(param_2 + 0x94);
  *(undefined4 *)(param_1 + 0x1c) = *(undefined4 *)(param_2 + 0x98);
  param_1[0x20] = *(ExtCamInfo *)(param_2 + 0x9c);
  *(undefined4 *)(param_1 + 0x24) = *(undefined4 *)(param_2 + 0xa0);
  param_1[0x28] = *(ExtCamInfo *)(param_2 + 0xa4);
  *(undefined2 *)(param_1 + 0x2a) = *(undefined2 *)(param_2 + 0xa6);
  param_1[0x2c] = *(ExtCamInfo *)(param_2 + 0xa8);
  *(undefined4 *)(param_1 + 0x30) = *(undefined4 *)(param_2 + 0xac);
  *(undefined4 *)(param_1 + 0x34) = *(undefined4 *)(param_2 + 0xb0);
  param_1[0x38] = *(ExtCamInfo *)(param_2 + 0xb4);
  *(undefined4 *)(param_1 + 0x3c) = *(undefined4 *)(param_2 + 0xb8);
  param_1[0x40] = *(ExtCamInfo *)(param_2 + 0xbc);
  *(undefined4 *)(param_1 + 0x44) = *(undefined4 *)(param_2 + 0xc0);
  param_1[0x48] = *(ExtCamInfo *)(param_2 + 0xc4);
  *(undefined4 *)(param_1 + 0x4c) = *(undefined4 *)(param_2 + 200);
  param_1[0x50] = *(ExtCamInfo *)(param_2 + 0xcc);
  *(undefined4 *)(param_1 + 0x54) = *(undefined4 *)(param_2 + 0xd0);
  param_1[0x58] = *(ExtCamInfo *)(param_2 + 0xd4);
  *(undefined4 *)(param_1 + 0x5c) = *(undefined4 *)(param_2 + 0xd8);
  *(undefined4 *)(param_1 + 0x60) = *(undefined4 *)(param_2 + 0xdc);
  param_1[100] = *(ExtCamInfo *)(param_2 + 0xe0);
  *(undefined2 *)(param_1 + 0x66) = *(undefined2 *)(param_2 + 0xe2);
  param_1[0x68] = *(ExtCamInfo *)(param_2 + 0xe4);
  *(undefined2 *)(param_1 + 0x6a) = *(undefined2 *)(param_2 + 0xe6);
  param_1[0x6c] = *(ExtCamInfo *)(param_2 + 0xf1);
  *(undefined2 *)(param_1 + 0x6e) = *(undefined2 *)(param_2 + 0xf2);
  param_1[0x70] = *(ExtCamInfo *)(param_2 + 0xf4);
  *(undefined4 *)(param_1 + 0x74) = *(undefined4 *)(param_2 + 0xf8);
  return;
}


/* 0002d3e6 */

/* MprCnv::Exchg_GPSDateStamp(MPR::GPSDateStamp*, DefStruct::GPSDateStamp*) */

void MprCnv::Exchg_GPSDateStamp(GPSDateStamp *param_1,GPSDateStamp *param_2)

{
  *(undefined2 *)param_1 = *(undefined2 *)param_2;
  param_1[2] = *(GPSDateStamp *)(param_2 + 2);
  param_1[3] = *(GPSDateStamp *)(param_2 + 3);
  return;
}


/* 0002d3f8 */

/* MprCnv::Exchg_GPSDateStamp(DefStruct::GPSDateStamp*, MPR::GPSDateStamp*) */

void MprCnv::Exchg_GPSDateStamp(GPSDateStamp *param_1,GPSDateStamp *param_2)

{
  *(undefined2 *)param_1 = *(undefined2 *)param_2;
  param_1[2] = *(GPSDateStamp *)(param_2 + 2);
  param_1[3] = *(GPSDateStamp *)(param_2 + 3);
  return;
}


/* 0002d40a */

/* MprCnv::Exchg_RationalValue(MPR::RationalValue*, DefStruct::RationalValue*) */

void MprCnv::Exchg_RationalValue(RationalValue *param_1,RationalValue *param_2)

{
  undefined2 uVar1;
  
  uVar1 = *(undefined2 *)(param_2 + 2);
  *(undefined2 *)param_1 = *(undefined2 *)param_2;
  *(undefined2 *)(param_1 + 2) = uVar1;
  return;
}


/* 0002d418 */

/* MprCnv::Exchg_DegMinSec(MPR::DegMinSec*, DefStruct::DegMinSec*) */

void MprCnv::Exchg_DegMinSec(DegMinSec *param_1,DegMinSec *param_2)

{
  Exchg_RationalValue((RationalValue *)param_1,(RationalValue *)param_2);
  Exchg_RationalValue((RationalValue *)(param_1 + 4),(RationalValue *)(param_2 + 4));
  (*(code *)PTR_Exchg_RationalValue_0004beb0)(param_1 + 8,param_2 + 8);
  return;
}


/* 0002d43c */

/* MprCnv::Exchg_GPSTimeStamp(MPR::GPSTimeStamp*, DefStruct::GPSTimeStamp*) */

void MprCnv::Exchg_GPSTimeStamp(GPSTimeStamp *param_1,GPSTimeStamp *param_2)

{
  Exchg_RationalValue((RationalValue *)param_1,(RationalValue *)param_2);
  Exchg_RationalValue((RationalValue *)(param_1 + 4),(RationalValue *)(param_2 + 4));
  (*(code *)PTR_Exchg_RationalValue_0004beb0)(param_1 + 8,param_2 + 8);
  return;
}


/* 0002d460 */

/* MprCnv::Exchg_RationalValue(DefStruct::RationalValue*, MPR::RationalValue*) */

void MprCnv::Exchg_RationalValue(RationalValue *param_1,RationalValue *param_2)

{
  undefined2 uVar1;
  
  uVar1 = *(undefined2 *)(param_2 + 2);
  *(undefined2 *)param_1 = *(undefined2 *)param_2;
  *(undefined2 *)(param_1 + 2) = uVar1;
  return;
}


/* 0002d46e */

/* MprCnv::Exchg_DegMinSec(DefStruct::DegMinSec*, MPR::DegMinSec*) */

void MprCnv::Exchg_DegMinSec(DegMinSec *param_1,DegMinSec *param_2)

{
  Exchg_RationalValue((RationalValue *)param_1,(RationalValue *)param_2);
  Exchg_RationalValue((RationalValue *)(param_1 + 4),(RationalValue *)(param_2 + 4));
  (*(code *)PTR_Exchg_RationalValue_0004c034)(param_1 + 8,param_2 + 8);
  return;
}


/* 0002d492 */

/* MprCnv::Exchg_GPSTimeStamp(DefStruct::GPSTimeStamp*, MPR::GPSTimeStamp*) */

void MprCnv::Exchg_GPSTimeStamp(GPSTimeStamp *param_1,GPSTimeStamp *param_2)

{
  Exchg_RationalValue((RationalValue *)param_1,(RationalValue *)param_2);
  Exchg_RationalValue((RationalValue *)(param_1 + 4),(RationalValue *)(param_2 + 4));
  (*(code *)PTR_Exchg_RationalValue_0004c034)(param_1 + 8,param_2 + 8);
  return;
}


/* 0002d4b6 */

/* MprCnv::Exchg_SpeedRef(MPR::SpeedRef*, DefStruct::SpeedRef*) */

void MprCnv::Exchg_SpeedRef(SpeedRef *param_1,SpeedRef *param_2)

{
  int iVar1;
  
  iVar1 = *(int *)param_2;
  if (((iVar1 != 1) && (iVar1 != 2)) && (iVar1 != 0)) {
    iVar1 = 0;
  }
  *(int *)param_1 = iVar1;
  return;
}


/* 0002d4cc */

/* MprCnv::Exchg_SpeedRef(DefStruct::SpeedRef*, MPR::SpeedRef*) */

void MprCnv::Exchg_SpeedRef(SpeedRef *param_1,SpeedRef *param_2)

{
  int iVar1;
  
  iVar1 = *(int *)param_2;
  if (((iVar1 != 1) && (iVar1 != 2)) && (iVar1 != 0)) {
    iVar1 = 0;
  }
  *(int *)param_1 = iVar1;
  return;
}


/* 0002d4e2 */

/* MprCnv::Exchg_TrackRef(MPR::TrackRef*, DefStruct::TrackRef*) */

void MprCnv::Exchg_TrackRef(TrackRef *param_1,TrackRef *param_2)

{
  int iVar1;
  
  iVar1 = *(int *)param_2;
  if ((iVar1 != 0) && (iVar1 != 1)) {
    iVar1 = 0;
  }
  *(int *)param_1 = iVar1;
  return;
}


/* 0002d4f4 */

/* MprCnv::Exchg_TrackRef(DefStruct::TrackRef*, MPR::TrackRef*) */

void MprCnv::Exchg_TrackRef(TrackRef *param_1,TrackRef *param_2)

{
  int iVar1;
  
  iVar1 = *(int *)param_2;
  if ((iVar1 != 0) && (iVar1 != 1)) {
    iVar1 = 0;
  }
  *(int *)param_1 = iVar1;
  return;
}


/* 0002d506 */

/* MprCnv::Exchg_ImgDirectionRef(MPR::ImgDirectionRef*, DefStruct::ImgDirectionRef*) */

void MprCnv::Exchg_ImgDirectionRef(ImgDirectionRef *param_1,ImgDirectionRef *param_2)

{
  int iVar1;
  
  iVar1 = *(int *)param_2;
  if ((iVar1 != 0) && (iVar1 != 1)) {
    iVar1 = 0;
  }
  *(int *)param_1 = iVar1;
  return;
}


/* 0002d518 */

/* MprCnv::Exchg_ImgDirectionRef(DefStruct::ImgDirectionRef*, MPR::ImgDirectionRef*) */

void MprCnv::Exchg_ImgDirectionRef(ImgDirectionRef *param_1,ImgDirectionRef *param_2)

{
  int iVar1;
  
  iVar1 = *(int *)param_2;
  if ((iVar1 != 0) && (iVar1 != 1)) {
    iVar1 = 0;
  }
  *(int *)param_1 = iVar1;
  return;
}


/* 0002d52a */

/* MprCnv::Exchg_LatitudeRef(MPR::LatitudeRef*, DefStruct::LatitudeRef*) */

void MprCnv::Exchg_LatitudeRef(LatitudeRef *param_1,LatitudeRef *param_2)

{
  int iVar1;
  
  iVar1 = *(int *)param_2;
  if ((iVar1 != 0) && (iVar1 != 1)) {
    iVar1 = 0;
  }
  *(int *)param_1 = iVar1;
  return;
}


/* 0002d53c */

/* MprCnv::Exchg_LatitudeRef(DefStruct::LatitudeRef*, MPR::LatitudeRef*) */

void MprCnv::Exchg_LatitudeRef(LatitudeRef *param_1,LatitudeRef *param_2)

{
  int iVar1;
  
  iVar1 = *(int *)param_2;
  if ((iVar1 != 0) && (iVar1 != 1)) {
    iVar1 = 0;
  }
  *(int *)param_1 = iVar1;
  return;
}


/* 0002d54e */

/* MprCnv::Exchg_LongitudeRef(MPR::LongitudeRef*, DefStruct::LongitudeRef*) */

void MprCnv::Exchg_LongitudeRef(LongitudeRef *param_1,LongitudeRef *param_2)

{
  int iVar1;
  
  iVar1 = *(int *)param_2;
  if ((iVar1 != 0) && (iVar1 != 1)) {
    iVar1 = 0;
  }
  *(int *)param_1 = iVar1;
  return;
}


/* 0002d560 */

/* MprCnv::Exchg_LongitudeRef(DefStruct::LongitudeRef*, MPR::LongitudeRef*) */

void MprCnv::Exchg_LongitudeRef(LongitudeRef *param_1,LongitudeRef *param_2)

{
  int iVar1;
  
  iVar1 = *(int *)param_2;
  if ((iVar1 != 0) && (iVar1 != 1)) {
    iVar1 = 0;
  }
  *(int *)param_1 = iVar1;
  return;
}


/* 0002d572 */

/* MprCnv::Exchg_AltitudeRef(MPR::AltitudeRef*, DefStruct::AltitudeRef*) */

void MprCnv::Exchg_AltitudeRef(AltitudeRef *param_1,AltitudeRef *param_2)

{
  int iVar1;
  
  iVar1 = *(int *)param_2;
  if ((iVar1 != 0) && (iVar1 != 1)) {
    iVar1 = 0;
  }
  *(int *)param_1 = iVar1;
  return;
}


/* 0002d584 */

/* MprCnv::Exchg_AltitudeRef(DefStruct::AltitudeRef*, MPR::AltitudeRef*) */

void MprCnv::Exchg_AltitudeRef(AltitudeRef *param_1,AltitudeRef *param_2)

{
  int iVar1;
  
  iVar1 = *(int *)param_2;
  if ((iVar1 != 0) && (iVar1 != 1)) {
    iVar1 = 0;
  }
  *(int *)param_1 = iVar1;
  return;
}


/* 0002d596 */

/* MprCnv::Exchg_GpsStatus(MPR::GpsStatus*, DefStruct::GpsStatus*) */

void MprCnv::Exchg_GpsStatus(GpsStatus *param_1,GpsStatus *param_2)

{
  int iVar1;
  
  iVar1 = *(int *)param_2;
  if ((iVar1 != 0) && (iVar1 != 1)) {
    iVar1 = 0;
  }
  *(int *)param_1 = iVar1;
  return;
}


/* 0002d5a8 */

/* MprCnv::Exchg_GpsBasicInfo(MPR::GpsBasicInfo*, DefStruct::GpsBasicInfo*) */

void MprCnv::Exchg_GpsBasicInfo(GpsBasicInfo *param_1,GpsBasicInfo *param_2)

{
  Exchg_GpsStatus((GpsStatus *)param_1,(GpsStatus *)param_2);
  param_1[4] = *(GpsBasicInfo *)(param_2 + 4);
  Exchg_LatitudeRef((LatitudeRef *)(param_1 + 8),(LatitudeRef *)(param_2 + 8));
  Exchg_DegMinSec((DegMinSec *)(param_1 + 0xc),(DegMinSec *)(param_2 + 0xc));
  param_1[0x18] = *(GpsBasicInfo *)(param_2 + 0x18);
  Exchg_LongitudeRef((LongitudeRef *)(param_1 + 0x1c),(LongitudeRef *)(param_2 + 0x1c));
  (*(code *)PTR_Exchg_DegMinSec_0004c308)(param_1 + 0x20,param_2 + 0x20);
  return;
}


/* 0002d5f0 */

/* MprCnv::Exchg_GpsStatus(DefStruct::GpsStatus*, MPR::GpsStatus*) */

void MprCnv::Exchg_GpsStatus(GpsStatus *param_1,GpsStatus *param_2)

{
  int iVar1;
  
  iVar1 = *(int *)param_2;
  if ((iVar1 != 0) && (iVar1 != 1)) {
    iVar1 = 0;
  }
  *(int *)param_1 = iVar1;
  return;
}


/* 0002d602 */

/* MprCnv::Exchg_GpsBasicInfo(DefStruct::GpsBasicInfo*, MPR::GpsBasicInfo*) */

void MprCnv::Exchg_GpsBasicInfo(GpsBasicInfo *param_1,GpsBasicInfo *param_2)

{
  Exchg_GpsStatus((GpsStatus *)param_1,(GpsStatus *)param_2);
  param_1[4] = *(GpsBasicInfo *)(param_2 + 4);
  Exchg_LatitudeRef((LatitudeRef *)(param_1 + 8),(LatitudeRef *)(param_2 + 8));
  Exchg_DegMinSec((DegMinSec *)(param_1 + 0xc),(DegMinSec *)(param_2 + 0xc));
  param_1[0x18] = *(GpsBasicInfo *)(param_2 + 0x18);
  Exchg_LongitudeRef((LongitudeRef *)(param_1 + 0x1c),(LongitudeRef *)(param_2 + 0x1c));
  (*(code *)PTR_Exchg_DegMinSec_0004be88)(param_1 + 0x20,param_2 + 0x20);
  return;
}


/* 0002d64a */

/* MprCnv::Exchg_GpsMeasureMode(MPR::GpsMeasureMode*, DefStruct::GpsMeasureMode*) */

void MprCnv::Exchg_GpsMeasureMode(GpsMeasureMode *param_1,GpsMeasureMode *param_2)

{
  int iVar1;
  
  iVar1 = *(int *)param_2;
  if ((iVar1 != 0) && (iVar1 != 1)) {
    iVar1 = 0;
  }
  *(int *)param_1 = iVar1;
  return;
}


/* 0002d65c */

/* MprCnv::Exchg_GpsInfo(MPR::GpsInfo*, DefStruct::GpsInfo*) */

void MprCnv::Exchg_GpsInfo(GpsInfo *param_1,GpsInfo *param_2)

{
  *param_1 = *(GpsInfo *)param_2;
  MemUtil::MemCpy8(param_1 + 1,param_2 + 1,4);
  param_1[5] = *(GpsInfo *)(param_2 + 5);
  Exchg_LatitudeRef((LatitudeRef *)(param_1 + 8),(LatitudeRef *)(param_2 + 8));
  Exchg_DegMinSec((DegMinSec *)(param_1 + 0xc),(DegMinSec *)(param_2 + 0xc));
  param_1[0x18] = *(GpsInfo *)(param_2 + 0x18);
  Exchg_LongitudeRef((LongitudeRef *)(param_1 + 0x1c),(LongitudeRef *)(param_2 + 0x1c));
  Exchg_DegMinSec((DegMinSec *)(param_1 + 0x20),(DegMinSec *)(param_2 + 0x20));
  param_1[0x2c] = *(GpsInfo *)(param_2 + 0x2c);
  Exchg_AltitudeRef((AltitudeRef *)(param_1 + 0x30),(AltitudeRef *)(param_2 + 0x30));
  Exchg_RationalValue((RationalValue *)(param_1 + 0x34),(RationalValue *)(param_2 + 0x34));
  param_1[0x38] = *(GpsInfo *)(param_2 + 0x38);
  Exchg_GPSDateStamp((GPSDateStamp *)(param_1 + 0x3a),(GPSDateStamp *)(param_2 + 0x3a));
  param_1[0x3e] = *(GpsInfo *)(param_2 + 0x3e);
  Exchg_GPSTimeStamp((GPSTimeStamp *)(param_1 + 0x40),(GPSTimeStamp *)(param_2 + 0x40));
  param_1[0x4c] = *(GpsInfo *)(param_2 + 0x4c);
  Exchg_GpsStatus((GpsStatus *)(param_1 + 0x50),(GpsStatus *)(param_2 + 0x50));
  param_1[0x54] = *(GpsInfo *)(param_2 + 0x54);
  Exchg_GpsMeasureMode((GpsMeasureMode *)(param_1 + 0x58),(GpsMeasureMode *)(param_2 + 0x58));
  param_1[0x5c] = *(GpsInfo *)(param_2 + 0x5c);
  Exchg_RationalValue((RationalValue *)(param_1 + 0x5e),(RationalValue *)(param_2 + 0x5e));
  param_1[0x62] = *(GpsInfo *)(param_2 + 0x62);
  Exchg_SpeedRef((SpeedRef *)(param_1 + 100),(SpeedRef *)(param_2 + 100));
  Exchg_RationalValue((RationalValue *)(param_1 + 0x68),(RationalValue *)(param_2 + 0x68));
  param_1[0x6c] = *(GpsInfo *)(param_2 + 0x6c);
  Exchg_TrackRef((TrackRef *)(param_1 + 0x70),(TrackRef *)(param_2 + 0x70));
  Exchg_RationalValue((RationalValue *)(param_1 + 0x74),(RationalValue *)(param_2 + 0x74));
  param_1[0x78] = *(GpsInfo *)(param_2 + 0x78);
  Exchg_ImgDirectionRef((ImgDirectionRef *)(param_1 + 0x7c),(ImgDirectionRef *)(param_2 + 0x7c));
  Exchg_RationalValue((RationalValue *)(param_1 + 0x80),(RationalValue *)(param_2 + 0x80));
  param_1[0x84] = *(GpsInfo *)(param_2 + 0x84);
  (*(code *)PTR_MemCpy8_0004c1ec)(param_1 + 0x85,param_2 + 0x85,9);
  return;
}


/* 0002d7a8 */

/* MprCnv::Exchg_GpsMeasureMode(DefStruct::GpsMeasureMode*, MPR::GpsMeasureMode*) */

void MprCnv::Exchg_GpsMeasureMode(GpsMeasureMode *param_1,GpsMeasureMode *param_2)

{
  int iVar1;
  
  iVar1 = *(int *)param_2;
  if ((iVar1 != 0) && (iVar1 != 1)) {
    iVar1 = 0;
  }
  *(int *)param_1 = iVar1;
  return;
}


/* 0002d7ba */

/* MprCnv::Exchg_GpsInfo(DefStruct::GpsInfo*, MPR::GpsInfo*) */

void MprCnv::Exchg_GpsInfo(GpsInfo *param_1,GpsInfo *param_2)

{
  *param_1 = *(GpsInfo *)param_2;
  MemUtil::MemCpy8(param_1 + 1,param_2 + 1,4);
  param_1[5] = *(GpsInfo *)(param_2 + 5);
  Exchg_LatitudeRef((LatitudeRef *)(param_1 + 8),(LatitudeRef *)(param_2 + 8));
  Exchg_DegMinSec((DegMinSec *)(param_1 + 0xc),(DegMinSec *)(param_2 + 0xc));
  param_1[0x18] = *(GpsInfo *)(param_2 + 0x18);
  Exchg_LongitudeRef((LongitudeRef *)(param_1 + 0x1c),(LongitudeRef *)(param_2 + 0x1c));
  Exchg_DegMinSec((DegMinSec *)(param_1 + 0x20),(DegMinSec *)(param_2 + 0x20));
  param_1[0x2c] = *(GpsInfo *)(param_2 + 0x2c);
  Exchg_AltitudeRef((AltitudeRef *)(param_1 + 0x30),(AltitudeRef *)(param_2 + 0x30));
  Exchg_RationalValue((RationalValue *)(param_1 + 0x34),(RationalValue *)(param_2 + 0x34));
  param_1[0x38] = *(GpsInfo *)(param_2 + 0x38);
  Exchg_GPSDateStamp((GPSDateStamp *)(param_1 + 0x3a),(GPSDateStamp *)(param_2 + 0x3a));
  param_1[0x3e] = *(GpsInfo *)(param_2 + 0x3e);
  Exchg_GPSTimeStamp((GPSTimeStamp *)(param_1 + 0x40),(GPSTimeStamp *)(param_2 + 0x40));
  param_1[0x4c] = *(GpsInfo *)(param_2 + 0x4c);
  Exchg_GpsStatus((GpsStatus *)(param_1 + 0x50),(GpsStatus *)(param_2 + 0x50));
  param_1[0x54] = *(GpsInfo *)(param_2 + 0x54);
  Exchg_GpsMeasureMode((GpsMeasureMode *)(param_1 + 0x58),(GpsMeasureMode *)(param_2 + 0x58));
  param_1[0x5c] = *(GpsInfo *)(param_2 + 0x5c);
  Exchg_RationalValue((RationalValue *)(param_1 + 0x5e),(RationalValue *)(param_2 + 0x5e));
  param_1[0x62] = *(GpsInfo *)(param_2 + 0x62);
  Exchg_SpeedRef((SpeedRef *)(param_1 + 100),(SpeedRef *)(param_2 + 100));
  Exchg_RationalValue((RationalValue *)(param_1 + 0x68),(RationalValue *)(param_2 + 0x68));
  param_1[0x6c] = *(GpsInfo *)(param_2 + 0x6c);
  Exchg_TrackRef((TrackRef *)(param_1 + 0x70),(TrackRef *)(param_2 + 0x70));
  Exchg_RationalValue((RationalValue *)(param_1 + 0x74),(RationalValue *)(param_2 + 0x74));
  param_1[0x78] = *(GpsInfo *)(param_2 + 0x78);
  Exchg_ImgDirectionRef((ImgDirectionRef *)(param_1 + 0x7c),(ImgDirectionRef *)(param_2 + 0x7c));
  Exchg_RationalValue((RationalValue *)(param_1 + 0x80),(RationalValue *)(param_2 + 0x80));
  param_1[0x84] = *(GpsInfo *)(param_2 + 0x84);
  (*(code *)PTR_MemCpy8_0004c1ec)(param_1 + 0x85,param_2 + 0x85,9);
  return;
}


/* 0002d906 */

/* MprCnv::Exchg_HighlightRssTheme(MPR::HighlightTheme*, DefStruct::HighlightRssTheme*) */

void MprCnv::Exchg_HighlightRssTheme(HighlightTheme *param_1,HighlightRssTheme *param_2)

{
  undefined4 uVar1;
  
  switch(*(undefined4 *)param_2) {
  default:
    uVar1 = 0;
    break;
  case 1:
    uVar1 = 1;
    break;
  case 2:
    uVar1 = 2;
    break;
  case 3:
    uVar1 = 3;
  }
  *(undefined4 *)param_1 = uVar1;
  return;
}


/* 0002d92a */

/* MprCnv::Exchg_HighlightRssTheme(DefStruct::HighlightRssTheme*, MPR::HighlightTheme*) */

void MprCnv::Exchg_HighlightRssTheme(HighlightRssTheme *param_1,HighlightTheme *param_2)

{
  undefined4 uVar1;
  
  switch(*(undefined4 *)param_2) {
  default:
    uVar1 = 0;
    break;
  case 1:
    uVar1 = 1;
    break;
  case 2:
    uVar1 = 2;
    break;
  case 3:
    uVar1 = 3;
  }
  *(undefined4 *)param_1 = uVar1;
  return;
}


/* 0002d94e */

/* MprCnv::Exchg_HighlightMovieStatus(MPR::HighlightMovieStatus*, DefStruct::HighlightMovieStatus*)
    */

void MprCnv::Exchg_HighlightMovieStatus(HighlightMovieStatus *param_1,HighlightMovieStatus *param_2)

{
  undefined4 uVar1;
  
  switch(*(undefined4 *)param_2) {
  default:
    uVar1 = 0;
    break;
  case 1:
    uVar1 = 1;
    break;
  case 2:
    uVar1 = 2;
    break;
  case 3:
    uVar1 = 3;
  }
  *(undefined4 *)param_1 = uVar1;
  return;
}


/* 0002d972 */

/* MprCnv::Exchg_HighlightMovieStatus(DefStruct::HighlightMovieStatus*, MPR::HighlightMovieStatus*)
    */

void MprCnv::Exchg_HighlightMovieStatus(HighlightMovieStatus *param_1,HighlightMovieStatus *param_2)

{
  undefined4 uVar1;
  
  switch(*(undefined4 *)param_2) {
  default:
    uVar1 = 0;
    break;
  case 1:
    uVar1 = 1;
    break;
  case 2:
    uVar1 = 2;
    break;
  case 3:
    uVar1 = 3;
  }
  *(undefined4 *)param_1 = uVar1;
  return;
}


/* 0002d996 */

/* MprCnv::Exchg_HighlightMovieProperty(MPR::HighlightMovieProperty*,
   DefStruct::HighlightMovieProperty*) */

void MprCnv::Exchg_HighlightMovieProperty
               (HighlightMovieProperty *param_1,HighlightMovieProperty *param_2)

{
  Exchg_LocalTime((T_LTM *)param_1,(LocalTime *)param_2);
  Exchg_LocalTime((T_LTM *)(param_1 + 10),(LocalTime *)(param_2 + 10));
  Exchg_LocalTime((T_LTM *)(param_1 + 0x14),(LocalTime *)(param_2 + 0x14));
  Exchg_HighlightRssTheme((HighlightTheme *)(param_1 + 0x20),(HighlightRssTheme *)(param_2 + 0x20));
  param_1[0x24] = *(HighlightMovieProperty *)(param_2 + 0x24);
  *(undefined4 *)(param_1 + 0x28) = *(undefined4 *)(param_2 + 0x28);
  return;
}


/* 0002d9d4 */

/* MprCnv::Exchg_HighlightMovieProperty(DefStruct::HighlightMovieProperty*,
   MPR::HighlightMovieProperty*) */

void MprCnv::Exchg_HighlightMovieProperty
               (HighlightMovieProperty *param_1,HighlightMovieProperty *param_2)

{
  Exchg_LocalTime((LocalTime *)param_1,(T_LTM *)param_2);
  Exchg_LocalTime((LocalTime *)(param_1 + 10),(T_LTM *)(param_2 + 10));
  Exchg_LocalTime((LocalTime *)(param_1 + 0x14),(T_LTM *)(param_2 + 0x14));
  Exchg_HighlightRssTheme((HighlightRssTheme *)(param_1 + 0x20),(HighlightTheme *)(param_2 + 0x20));
  param_1[0x24] = *(HighlightMovieProperty *)(param_2 + 0x24);
  *(undefined4 *)(param_1 + 0x28) = *(undefined4 *)(param_2 + 0x28);
  return;
}


/* 0002da12 */

/* MprCnv::Exchg_HighlightMovieBgmProperty(MPR::HighlightMovieBgmProperty*,
   DefStruct::HighlightMovieBgmProperty*) */

void MprCnv::Exchg_HighlightMovieBgmProperty
               (HighlightMovieBgmProperty *param_1,HighlightMovieBgmProperty *param_2)

{
  *param_1 = *(HighlightMovieBgmProperty *)param_2;
  *(undefined4 *)(param_1 + 0xc) = *(undefined4 *)(param_2 + 4);
  *(undefined4 *)(param_1 + 0x10) = *(undefined4 *)(param_2 + 8);
  return;
}


/* 0002da24 */

/* MprCnv::Exchg_HighlightMovieBgmProperty(DefStruct::HighlightMovieBgmProperty*,
   MPR::HighlightMovieBgmProperty*) */

void MprCnv::Exchg_HighlightMovieBgmProperty
               (HighlightMovieBgmProperty *param_1,HighlightMovieBgmProperty *param_2)

{
  *param_1 = *(HighlightMovieBgmProperty *)param_2;
  *(undefined4 *)(param_1 + 4) = *(undefined4 *)(param_2 + 0xc);
  *(undefined4 *)(param_1 + 8) = *(undefined4 *)(param_2 + 0x10);
  return;
}


/* 0002da36 */

/* MprCnv::Exchg_ContentType(MPR::ContentType*, DefStruct::ContentType*) */

void MprCnv::Exchg_ContentType(ContentType *param_1,ContentType *param_2)

{
  undefined4 uVar1;
  
  switch(*(undefined4 *)param_2) {
  case 0:
    uVar1 = 0x20;
    break;
  case 1:
    uVar1 = 0x10;
    break;
  case 2:
    uVar1 = 8;
    break;
  case 3:
    uVar1 = 6;
    break;
  case 4:
    uVar1 = 1;
    break;
  case 5:
    uVar1 = 0x40;
    break;
  default:
    uVar1 = 0;
    break;
  case 7:
    uVar1 = 0x100;
    break;
  case 8:
    uVar1 = 0x200;
  }
  *(undefined4 *)param_1 = uVar1;
  return;
}


/* 0002da78 */

/* MprCnv::Exchg_ContentType(DefStruct::ContentType*, MPR::ContentType*) */

void MprCnv::Exchg_ContentType(ContentType *param_1,ContentType *param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = *(int *)param_2;
  if (iVar1 == 0x10) {
    uVar2 = 1;
    goto LAB_0002dace;
  }
  if (iVar1 < 0x11) {
    if (iVar1 == 6) {
      uVar2 = 3;
      goto LAB_0002dace;
    }
    if (iVar1 == 8) {
      uVar2 = 2;
      goto LAB_0002dace;
    }
    if (iVar1 == 1) {
      uVar2 = 4;
      goto LAB_0002dace;
    }
  }
  else {
    if (iVar1 == 0x40) {
      uVar2 = 5;
      goto LAB_0002dace;
    }
    if (iVar1 < 0x41) {
      if (iVar1 == 0x20) {
        uVar2 = 0;
        goto LAB_0002dace;
      }
    }
    else {
      if (iVar1 == 0x100) {
        uVar2 = 7;
        goto LAB_0002dace;
      }
      if (iVar1 == 0x200) {
        uVar2 = 8;
        goto LAB_0002dace;
      }
    }
  }
  uVar2 = 0xff;
LAB_0002dace:
  *(undefined4 *)param_1 = uVar2;
  return;
}


/* 0002dad2 */

/* MprCnv::Exchg_DcfFileType(MPR::StillFileType*, DefStruct::DcfFileType*) */

void MprCnv::Exchg_DcfFileType(StillFileType *param_1,DcfFileType *param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = *(int *)param_2;
  if (iVar1 == 2) {
    uVar2 = 1;
  }
  else if (iVar1 == 4) {
    uVar2 = 2;
  }
  else if (iVar1 == 1) {
    uVar2 = 0;
  }
  else {
    uVar2 = 0xff;
  }
  *(undefined4 *)param_1 = uVar2;
  return;
}


/* 0002daf6 */

/* MprCnv::Exchg_DcfFileType(DefStruct::DcfFileType*, MPR::StillFileType*) */

void MprCnv::Exchg_DcfFileType(DcfFileType *param_1,StillFileType *param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = *(int *)param_2;
  if (iVar1 == 1) {
    uVar2 = 2;
  }
  else if (iVar1 == 2) {
    uVar2 = 4;
  }
  else if (iVar1 == 0) {
    uVar2 = 1;
  }
  else {
    uVar2 = 0;
  }
  *(undefined4 *)param_1 = uVar2;
  return;
}


/* 0002db18 */

/* MprCnv::Exchg_ResumePoint(MPR::RSMPoint*, DefStruct::ResumePoint*) */

void MprCnv::Exchg_ResumePoint(RSMPoint *param_1,ResumePoint *param_2)

{
  (*(code *)PTR_MemCpy8_0004c1ec)(param_1,param_2,0x40);
  return;
}


/* 0002db26 */

/* MprCnv::Exchg_ResumePoint(DefStruct::ResumePoint*, MPR::RSMPoint*) */

void MprCnv::Exchg_ResumePoint(ResumePoint *param_1,RSMPoint *param_2)

{
  (*(code *)PTR_MemCpy8_0004c1ec)(param_1,param_2,0x40);
  return;
}


/* 0002db34 */

/* MprCnv::Exchg_AreaInfo(MPR::AreaInfo*, DefStruct::AreaInfo const*) */

void MprCnv::Exchg_AreaInfo(AreaInfo *param_1,AreaInfo *param_2)

{
  *(undefined2 *)param_1 = *(undefined2 *)param_2;
  *(undefined4 *)(param_1 + 4) = *(undefined4 *)(param_2 + 4);
  *(undefined4 *)(param_1 + 8) = *(undefined4 *)(param_2 + 8);
  return;
}


/* 0002db46 */

/* MprCnv::Exchg_AreaInfo(DefStruct::AreaInfo*, MPR::AreaInfo const*) */

void MprCnv::Exchg_AreaInfo(AreaInfo *param_1,AreaInfo *param_2)

{
  *(uint *)param_1 = (uint)*(ushort *)param_2;
  *(undefined4 *)(param_1 + 4) = *(undefined4 *)(param_2 + 4);
  *(undefined4 *)(param_1 + 8) = *(undefined4 *)(param_2 + 8);
  return;
}


/* 0002db58 */

/* MprCnv::Exchg_ExifSrcInfo(MPR::ExifSrcInfo*, DefStruct::ExifSrcInfo const*) */

void MprCnv::Exchg_ExifSrcInfo(ExifSrcInfo *param_1,ExifSrcInfo *param_2)

{
  Exchg_AreaInfo((AreaInfo *)param_1,(AreaInfo *)param_2);
  Exchg_AreaInfo((AreaInfo *)(param_1 + 0xc),(AreaInfo *)(param_2 + 0x10));
  Exchg_AreaInfo((AreaInfo *)(param_1 + 0x18),(AreaInfo *)(param_2 + 0x20));
  Exchg_AreaInfo((AreaInfo *)(param_1 + 0x24),(AreaInfo *)(param_2 + 0x30));
  Exchg_AreaInfo((AreaInfo *)(param_1 + 0x30),(AreaInfo *)(param_2 + 0x40));
  Exchg_AreaInfo((AreaInfo *)(param_1 + 0x3c),(AreaInfo *)(param_2 + 0x50));
  Exchg_AreaInfo((AreaInfo *)(param_1 + 0x48),(AreaInfo *)(param_2 + 0x60));
  (*(code *)PTR_Exchg_AreaInfo_0004bfe0)(param_1 + 0x54,param_2 + 0x70);
  return;
}


/* 0002dbbc */

/* MprCnv::Exchg_ExifSrcInfo(DefStruct::ExifSrcInfo*, MPR::ExifSrcInfo const*) */

void MprCnv::Exchg_ExifSrcInfo(ExifSrcInfo *param_1,ExifSrcInfo *param_2)

{
  Exchg_AreaInfo((AreaInfo *)param_1,(AreaInfo *)param_2);
  Exchg_AreaInfo((AreaInfo *)(param_1 + 0x10),(AreaInfo *)(param_2 + 0xc));
  Exchg_AreaInfo((AreaInfo *)(param_1 + 0x20),(AreaInfo *)(param_2 + 0x18));
  Exchg_AreaInfo((AreaInfo *)(param_1 + 0x30),(AreaInfo *)(param_2 + 0x24));
  Exchg_AreaInfo((AreaInfo *)(param_1 + 0x40),(AreaInfo *)(param_2 + 0x30));
  Exchg_AreaInfo((AreaInfo *)(param_1 + 0x50),(AreaInfo *)(param_2 + 0x3c));
  Exchg_AreaInfo((AreaInfo *)(param_1 + 0x60),(AreaInfo *)(param_2 + 0x48));
  (*(code *)PTR_Exchg_AreaInfo_0004c18c)(param_1 + 0x70,param_2 + 0x54);
  return;
}


/* 0002dc20 */

/* MprCnv::Exchg_JpgInfo(MPR::JpgInfo*, DefStruct::JpgInfo const*) */

void MprCnv::Exchg_JpgInfo(JpgInfo *param_1,JpgInfo *param_2)

{
  Exchg_ExifSrcInfo((ExifSrcInfo *)param_1,(ExifSrcInfo *)param_2);
  Exchg_AreaInfo((AreaInfo *)(param_1 + 0x60),(AreaInfo *)(param_2 + 0x80));
  Exchg_AreaInfo((AreaInfo *)(param_1 + 0x6c),(AreaInfo *)(param_2 + 0x90));
  (*(code *)PTR_Exchg_AreaInfo_0004bfe0)(param_1 + 0x78,param_2 + 0xa0);
  return;
}


/* 0002dc54 */

/* MprCnv::Exchg_JpgInfo(DefStruct::JpgInfo*, MPR::JpgInfo const*) */

void MprCnv::Exchg_JpgInfo(JpgInfo *param_1,JpgInfo *param_2)

{
  Exchg_ExifSrcInfo((ExifSrcInfo *)param_1,(ExifSrcInfo *)param_2);
  Exchg_AreaInfo((AreaInfo *)(param_1 + 0x80),(AreaInfo *)(param_2 + 0x60));
  Exchg_AreaInfo((AreaInfo *)(param_1 + 0x90),(AreaInfo *)(param_2 + 0x6c));
  (*(code *)PTR_Exchg_AreaInfo_0004c18c)(param_1 + 0xa0,param_2 + 0x78);
  return;
}


/* 0002dc88 */

/* MprCnv::Exchg_MpoInfo(MPR::MpoInfo*, DefStruct::MpoInfo const*) */

void MprCnv::Exchg_MpoInfo(MpoInfo *param_1,MpoInfo *param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  *(undefined4 *)param_1 = *(undefined4 *)param_2;
  *(undefined4 *)(param_1 + 4) = *(undefined4 *)(param_2 + 4);
  do {
    iVar1 = iVar3 * 0x84;
    iVar2 = iVar3 * 0xb0;
    iVar3 = iVar3 + 1;
    Exchg_JpgInfo((JpgInfo *)(param_1 + iVar1 + 8),(JpgInfo *)(param_2 + iVar2 + 8));
  } while (iVar3 != 0xf);
  return;
}


/* 0002dcb6 */

/* MprCnv::Exchg_DevelopSrcInfo(MPR::DevelopSrcInfo*, DefStruct::DevelopSrcInfo const*) */

void MprCnv::Exchg_DevelopSrcInfo(DevelopSrcInfo *param_1,DevelopSrcInfo *param_2)

{
  Exchg_AreaInfo((AreaInfo *)param_1,(AreaInfo *)param_2);
  Exchg_AreaInfo((AreaInfo *)(param_1 + 0xc),(AreaInfo *)(param_2 + 0x10));
  Exchg_AreaInfo((AreaInfo *)(param_1 + 0x18),(AreaInfo *)(param_2 + 0x20));
  Exchg_AreaInfo((AreaInfo *)(param_1 + 0x24),(AreaInfo *)(param_2 + 0x30));
  Exchg_AreaInfo((AreaInfo *)(param_1 + 0x30),(AreaInfo *)(param_2 + 0x40));
  (*(code *)PTR_Exchg_AreaInfo_0004bfe0)(param_1 + 0x3c,param_2 + 0x50);
  return;
}


/* 0002dd02 */

/* MprCnv::Exchg_RawInfo(MPR::RawInfo*, DefStruct::RawInfo const*) */

void MprCnv::Exchg_RawInfo(RawInfo *param_1,RawInfo *param_2)

{
  Exchg_ExifSrcInfo((ExifSrcInfo *)param_1,(ExifSrcInfo *)param_2);
  Exchg_AreaInfo((AreaInfo *)(param_1 + 0x60),(AreaInfo *)(param_2 + 0x80));
  Exchg_DevelopSrcInfo((DevelopSrcInfo *)(param_1 + 0x6c),(DevelopSrcInfo *)(param_2 + 0x90));
  Exchg_AreaInfo((AreaInfo *)(param_1 + 0xb4),(AreaInfo *)(param_2 + 0xf0));
  (*(code *)PTR_Exchg_AreaInfo_0004bfe0)(param_1 + 0xc0,param_2 + 0x100);
  return;
}


/* 0002dd42 */

/* MprObjectUtil::MwfException::MwfException(MWF::ErrCd, unsigned int) */

void __thiscall
MprObjectUtil::MwfException::MwfException(MwfException *this,undefined4 param_2,undefined4 param_3)

{
  *(undefined4 *)this = param_2;
  *(undefined4 *)(this + 4) = param_3;
  return;
}


/* 0002dd4c */

/* MprObjectUtil::MwfUInt64(MWF::ObjMsg*, unsigned int) */

void MprObjectUtil::MwfUInt64(ObjMsg *param_1,uint param_2)

{
  MwfException *pMVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = DAT_0002ddb4 + 0x2dd5c;
  if (param_1 == (ObjMsg *)0x0) {
    pMVar1 = (MwfException *)__cxa_allocate_exception(8);
    MwfException::MwfException(pMVar1,3,param_2);
                    /* WARNING: Subroutine does not return */
    __cxa_throw(pMVar1,*(undefined4 *)(iVar3 + DAT_0002ddb8),0);
  }
  iVar2 = MWF::ObjMsg::GetParam(param_1,param_2,0x22);
  if (iVar2 == 0) {
    pMVar1 = (MwfException *)__cxa_allocate_exception(8);
    MwfException::MwfException(pMVar1,3,param_2);
                    /* WARNING: Subroutine does not return */
    __cxa_throw(pMVar1,*(undefined4 *)(iVar3 + DAT_0002ddb8),0);
  }
  MWF::UInt64::GetValue();
  return;
}


/* 0002ddbc */

/* MprObjectUtil::MwfUInt64(MWF::ObjMsg*, unsigned long long*, unsigned int) */

undefined4 MprObjectUtil::MwfUInt64(ObjMsg *param_1,ulonglong *param_2,uint param_3)

{
  ulonglong uVar1;
  
  uVar1 = MwfUInt64(param_1,param_3);
  *param_2 = uVar1;
  return 1;
}


/* 0002dde4 */

/* MprObjectUtil::MwfInt64(MWF::ObjMsg*, unsigned int) */

void MprObjectUtil::MwfInt64(ObjMsg *param_1,uint param_2)

{
  MwfException *pMVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = DAT_0002de4c + 0x2ddf4;
  if (param_1 == (ObjMsg *)0x0) {
    pMVar1 = (MwfException *)__cxa_allocate_exception(8);
    MwfException::MwfException(pMVar1,3,param_2);
                    /* WARNING: Subroutine does not return */
    __cxa_throw(pMVar1,*(undefined4 *)(iVar3 + DAT_0002de50),0);
  }
  iVar2 = MWF::ObjMsg::GetParam(param_1,param_2,0x21);
  if (iVar2 == 0) {
    pMVar1 = (MwfException *)__cxa_allocate_exception(8);
    MwfException::MwfException(pMVar1,3,param_2);
                    /* WARNING: Subroutine does not return */
    __cxa_throw(pMVar1,*(undefined4 *)(iVar3 + DAT_0002de50),0);
  }
  MWF::Int64::GetValue();
  return;
}


/* 0002de54 */

/* MprObjectUtil::MwfInt64(MWF::ObjMsg*, long long*, unsigned int) */

undefined4 MprObjectUtil::MwfInt64(ObjMsg *param_1,longlong *param_2,uint param_3)

{
  longlong lVar1;
  
  lVar1 = MwfInt64(param_1,param_3);
  *param_2 = lVar1;
  return 1;
}


/* 0002de7c */

/* MprObjectUtil::MwfUInt32(MWF::ObjMsg*, unsigned int) */

void MprObjectUtil::MwfUInt32(ObjMsg *param_1,uint param_2)

{
  MwfException *pMVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = DAT_0002dee4 + 0x2de8c;
  if (param_1 == (ObjMsg *)0x0) {
    pMVar1 = (MwfException *)__cxa_allocate_exception(8);
    MwfException::MwfException(pMVar1,3,param_2);
                    /* WARNING: Subroutine does not return */
    __cxa_throw(pMVar1,*(undefined4 *)(iVar3 + DAT_0002dee8),0);
  }
  iVar2 = MWF::ObjMsg::GetParam(param_1,param_2,8);
  if (iVar2 == 0) {
    pMVar1 = (MwfException *)__cxa_allocate_exception(8);
    MwfException::MwfException(pMVar1,3,param_2);
                    /* WARNING: Subroutine does not return */
    __cxa_throw(pMVar1,*(undefined4 *)(iVar3 + DAT_0002dee8),0);
  }
  MWF::ParamStd_Template<unsigned_int,(MWF::Param::Type)8>::GetValue();
  return;
}


/* 0002deec */

/* MprObjectUtil::MwfUInt32(MWF::ObjMsg*, unsigned int*, unsigned int) */

undefined4 MprObjectUtil::MwfUInt32(ObjMsg *param_1,uint *param_2,uint param_3)

{
  uint uVar1;
  
  uVar1 = MwfUInt32(param_1,param_3);
  *param_2 = uVar1;
  return 1;
}


/* 0002df14 */

/* MprObjectUtil::MwfInt32(MWF::ObjMsg*, unsigned int) */

void MprObjectUtil::MwfInt32(ObjMsg *param_1,uint param_2)

{
  MwfException *pMVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = DAT_0002df7c + 0x2df24;
  if (param_1 == (ObjMsg *)0x0) {
    pMVar1 = (MwfException *)__cxa_allocate_exception(8);
    MwfException::MwfException(pMVar1,3,param_2);
                    /* WARNING: Subroutine does not return */
    __cxa_throw(pMVar1,*(undefined4 *)(iVar3 + DAT_0002df80),0);
  }
  iVar2 = MWF::ObjMsg::GetParam(param_1,param_2,7);
  if (iVar2 == 0) {
    pMVar1 = (MwfException *)__cxa_allocate_exception(8);
    MwfException::MwfException(pMVar1,3,param_2);
                    /* WARNING: Subroutine does not return */
    __cxa_throw(pMVar1,*(undefined4 *)(iVar3 + DAT_0002df80),0);
  }
  MWF::ParamStd_Template<int,(MWF::Param::Type)7>::GetValue();
  return;
}


/* 0002df84 */

/* MprObjectUtil::MwfInt32(MWF::ObjMsg*, int*, unsigned int) */

undefined4 MprObjectUtil::MwfInt32(ObjMsg *param_1,int *param_2,uint param_3)

{
  int iVar1;
  
  iVar1 = MwfInt32(param_1,param_3);
  *param_2 = iVar1;
  return 1;
}


/* 0002dfac */

/* MprObjectUtil::MwfUInt16(MWF::ObjMsg*, unsigned int) */

void MprObjectUtil::MwfUInt16(ObjMsg *param_1,uint param_2)

{
  MwfException *pMVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = DAT_0002e014 + 0x2dfbc;
  if (param_1 == (ObjMsg *)0x0) {
    pMVar1 = (MwfException *)__cxa_allocate_exception(8);
    MwfException::MwfException(pMVar1,3,param_2);
                    /* WARNING: Subroutine does not return */
    __cxa_throw(pMVar1,*(undefined4 *)(iVar3 + DAT_0002e018),0);
  }
  iVar2 = MWF::ObjMsg::GetParam(param_1,param_2,6);
  if (iVar2 == 0) {
    pMVar1 = (MwfException *)__cxa_allocate_exception(8);
    MwfException::MwfException(pMVar1,3,param_2);
                    /* WARNING: Subroutine does not return */
    __cxa_throw(pMVar1,*(undefined4 *)(iVar3 + DAT_0002e018),0);
  }
  MWF::ParamStd_Template<unsigned_short,(MWF::Param::Type)6>::GetValue();
  return;
}


/* 0002e01c */

/* MprObjectUtil::MwfUInt16(MWF::ObjMsg*, unsigned short*, unsigned int) */

undefined4 MprObjectUtil::MwfUInt16(ObjMsg *param_1,ushort *param_2,uint param_3)

{
  ushort uVar1;
  
  uVar1 = MwfUInt16(param_1,param_3);
  *param_2 = uVar1;
  return 1;
}


/* 0002e044 */

/* MprObjectUtil::MwfInt16(MWF::ObjMsg*, unsigned int) */

void MprObjectUtil::MwfInt16(ObjMsg *param_1,uint param_2)

{
  MwfException *pMVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = DAT_0002e0ac + 0x2e054;
  if (param_1 == (ObjMsg *)0x0) {
    pMVar1 = (MwfException *)__cxa_allocate_exception(8);
    MwfException::MwfException(pMVar1,3,param_2);
                    /* WARNING: Subroutine does not return */
    __cxa_throw(pMVar1,*(undefined4 *)(iVar3 + DAT_0002e0b0),0);
  }
  iVar2 = MWF::ObjMsg::GetParam(param_1,param_2,5);
  if (iVar2 == 0) {
    pMVar1 = (MwfException *)__cxa_allocate_exception(8);
    MwfException::MwfException(pMVar1,3,param_2);
                    /* WARNING: Subroutine does not return */
    __cxa_throw(pMVar1,*(undefined4 *)(iVar3 + DAT_0002e0b0),0);
  }
  MWF::ParamStd_Template<short,(MWF::Param::Type)5>::GetValue();
  return;
}


/* 0002e0b4 */

/* MprObjectUtil::MwfInt16(MWF::ObjMsg*, short*, unsigned int) */

undefined4 MprObjectUtil::MwfInt16(ObjMsg *param_1,short *param_2,uint param_3)

{
  short sVar1;
  
  sVar1 = MwfInt16(param_1,param_3);
  *param_2 = sVar1;
  return 1;
}


/* 0002e0dc */

/* MprObjectUtil::MwfUInt8(MWF::ObjMsg*, unsigned int) */

void MprObjectUtil::MwfUInt8(ObjMsg *param_1,uint param_2)

{
  MwfException *pMVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = DAT_0002e144 + 0x2e0ec;
  if (param_1 == (ObjMsg *)0x0) {
    pMVar1 = (MwfException *)__cxa_allocate_exception(8);
    MwfException::MwfException(pMVar1,3,param_2);
                    /* WARNING: Subroutine does not return */
    __cxa_throw(pMVar1,*(undefined4 *)(iVar3 + DAT_0002e148),0);
  }
  iVar2 = MWF::ObjMsg::GetParam(param_1,param_2,4);
  if (iVar2 == 0) {
    pMVar1 = (MwfException *)__cxa_allocate_exception(8);
    MwfException::MwfException(pMVar1,3,param_2);
                    /* WARNING: Subroutine does not return */
    __cxa_throw(pMVar1,*(undefined4 *)(iVar3 + DAT_0002e148),0);
  }
  MWF::ParamStd_Template<unsigned_char,(MWF::Param::Type)4>::GetValue();
  return;
}


/* 0002e14c */

/* MprObjectUtil::MwfUInt8(MWF::ObjMsg*, unsigned char*, unsigned int) */

undefined4 MprObjectUtil::MwfUInt8(ObjMsg *param_1,uchar *param_2,uint param_3)

{
  uchar uVar1;
  
  uVar1 = MwfUInt8(param_1,param_3);
  *param_2 = uVar1;
  return 1;
}


/* 0002e174 */

/* MprObjectUtil::MwfInt8(MWF::ObjMsg*, unsigned int) */

void MprObjectUtil::MwfInt8(ObjMsg *param_1,uint param_2)

{
  MwfException *pMVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = DAT_0002e1dc + 0x2e184;
  if (param_1 == (ObjMsg *)0x0) {
    pMVar1 = (MwfException *)__cxa_allocate_exception(8);
    MwfException::MwfException(pMVar1,3,param_2);
                    /* WARNING: Subroutine does not return */
    __cxa_throw(pMVar1,*(undefined4 *)(iVar3 + DAT_0002e1e0),0);
  }
  iVar2 = MWF::ObjMsg::GetParam(param_1,param_2,3);
  if (iVar2 == 0) {
    pMVar1 = (MwfException *)__cxa_allocate_exception(8);
    MwfException::MwfException(pMVar1,3,param_2);
                    /* WARNING: Subroutine does not return */
    __cxa_throw(pMVar1,*(undefined4 *)(iVar3 + DAT_0002e1e0),0);
  }
  MWF::ParamStd_Template<signed_char,(MWF::Param::Type)3>::GetValue();
  return;
}


/* 0002e1e4 */

/* MprObjectUtil::MwfInt8(MWF::ObjMsg*, signed char*, unsigned int) */

undefined4 MprObjectUtil::MwfInt8(ObjMsg *param_1,signed *param_2,uint param_3)

{
  signed sVar1;
  
  sVar1 = (signed)MwfInt8(param_1,param_3);
  *param_2 = sVar1;
  return 1;
}


/* 0002e20c */

/* MprObjectUtil::MwfBool(MWF::ObjMsg*, unsigned int) */

void MprObjectUtil::MwfBool(ObjMsg *param_1,uint param_2)

{
  MwfException *pMVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = DAT_0002e274 + 0x2e21c;
  if (param_1 == (ObjMsg *)0x0) {
    pMVar1 = (MwfException *)__cxa_allocate_exception(8);
    MwfException::MwfException(pMVar1,3,param_2);
                    /* WARNING: Subroutine does not return */
    __cxa_throw(pMVar1,*(undefined4 *)(iVar3 + DAT_0002e278),0);
  }
  iVar2 = MWF::ObjMsg::GetParam(param_1,param_2,1);
  if (iVar2 == 0) {
    pMVar1 = (MwfException *)__cxa_allocate_exception(8);
    MwfException::MwfException(pMVar1,3,param_2);
                    /* WARNING: Subroutine does not return */
    __cxa_throw(pMVar1,*(undefined4 *)(iVar3 + DAT_0002e278),0);
  }
  MWF::ParamStd_Template<bool,(MWF::Param::Type)1>::GetValue();
  return;
}


/* 0002e27c */

/* MprObjectUtil::MwfBool(MWF::ObjMsg*, bool*, unsigned int) */

undefined4 MprObjectUtil::MwfBool(ObjMsg *param_1,bool *param_2,uint param_3)

{
  bool bVar1;
  
  bVar1 = (bool)MwfBool(param_1,param_3);
  *param_2 = bVar1;
  return 1;
}


/* 0002e2a4 */

/* MprObjectUtil::MwfStruct(MWF::ObjMsg*, unsigned int, unsigned int) */

void MprObjectUtil::MwfStruct(ObjMsg *param_1,uint param_2,uint param_3)

{
  MwfException *pMVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  
  iVar4 = DAT_0002e338 + 0x2e2b6;
  if (param_1 == (ObjMsg *)0x0) {
    pMVar1 = (MwfException *)__cxa_allocate_exception(8);
    MwfException::MwfException(pMVar1,3,param_2);
                    /* WARNING: Subroutine does not return */
    __cxa_throw(pMVar1,*(undefined4 *)(iVar4 + DAT_0002e33c),0);
  }
  iVar2 = MWF::ObjMsg::GetParam(param_1,param_2,0x28);
  if (iVar2 == 0) {
    pMVar1 = (MwfException *)__cxa_allocate_exception(8);
    MwfException::MwfException(pMVar1,3,param_2);
                    /* WARNING: Subroutine does not return */
    __cxa_throw(pMVar1,*(undefined4 *)(iVar4 + DAT_0002e33c),0);
  }
  uVar3 = MWF::Struct::GetSize();
  if (uVar3 < param_3) {
    pMVar1 = (MwfException *)__cxa_allocate_exception(8);
    MwfException::MwfException(pMVar1,0x6001,param_2);
                    /* WARNING: Subroutine does not return */
    __cxa_throw(pMVar1,*(undefined4 *)(iVar4 + DAT_0002e33c),0);
  }
  MWF::Struct::GetValue();
  return;
}


/* 0002e340 */

/* MprObjectUtil::MwfStruct(MWF::ObjMsg*, void**, unsigned int, unsigned int) */

undefined4 MprObjectUtil::MwfStruct(ObjMsg *param_1,void **param_2,uint param_3,uint param_4)

{
  void *pvVar1;
  
  pvVar1 = (void *)MwfStruct(param_1,param_3,param_4);
  *param_2 = pvVar1;
  return 1;
}


/* 0002e368 */

/* MprObjectUtil::MwfObjMsg(MWF::ObjMsg*, unsigned int) */

void MprObjectUtil::MwfObjMsg(ObjMsg *param_1,uint param_2)

{
  MwfException *pMVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = DAT_0002e3cc + 0x2e378;
  if (param_1 == (ObjMsg *)0x0) {
    pMVar1 = (MwfException *)__cxa_allocate_exception(8);
    MwfException::MwfException(pMVar1,3,param_2);
                    /* WARNING: Subroutine does not return */
    __cxa_throw(pMVar1,*(undefined4 *)(iVar3 + DAT_0002e3d0),0);
  }
  iVar2 = MWF::ObjMsg::GetParam(param_1,param_2,0x29);
  if (iVar2 == 0) {
    pMVar1 = (MwfException *)__cxa_allocate_exception(8);
    MwfException::MwfException(pMVar1,3,param_2);
                    /* WARNING: Subroutine does not return */
    __cxa_throw(pMVar1,*(undefined4 *)(iVar3 + DAT_0002e3d0),0);
  }
  return;
}


/* 0002e3d4 */

/* MprObjectUtil::MwfObjMsg(MWF::ObjMsg*, MWF::ObjMsg**, unsigned int) */

undefined4 MprObjectUtil::MwfObjMsg(ObjMsg *param_1,ObjMsg **param_2,uint param_3)

{
  ObjMsg *pOVar1;
  
  pOVar1 = (ObjMsg *)MwfObjMsg(param_1,param_3);
  *param_2 = pOVar1;
  return 1;
}


/* 0002e3fa */

/* StopWatch::Start(StopWatch::Time*) */

void StopWatch::Start(Time *param_1)

{
  longlong lVar1;
  
  *(undefined4 *)param_1 = 0xffffffff;
  *(undefined4 *)(param_1 + 4) = 0xffffffff;
  *(undefined4 *)(param_1 + 8) = 0xffffffff;
  *(undefined4 *)(param_1 + 0xc) = 0xffffffff;
  lVar1 = UtimeWrapper::GetSysCnt();
  if (lVar1 == 0) {
    lVar1 = -1;
  }
  *(longlong *)param_1 = lVar1;
  return;
}


/* 0002e42c */

/* StopWatch::GetTime(StopWatch::Time*, StopWatch::SWType) */

undefined4 StopWatch::GetTime(uint *param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  uint uVar6;
  bool bVar7;
  undefined8 uVar8;
  
  uVar6 = *param_1;
  if (uVar6 == 0xffffffff && param_1[1] == 0xffffffff) {
    return 0xffffffff;
  }
  uVar1 = param_1[2];
  if (uVar1 == 0xffffffff && param_1[3] == 0xffffffff) {
    return 0xffffffff;
  }
  uVar2 = uVar1 - uVar6;
  iVar5 = (param_1[3] - param_1[1]) - (uint)(uVar1 < uVar6);
  uVar8 = CONCAT44(iVar5,uVar2);
  if (param_2 == 0) {
    bVar7 = CARRY4(uVar2,DAT_0002e4a0);
    iVar3 = uVar2 + DAT_0002e4a0;
    uVar4 = DAT_0002e4a4;
  }
  else {
    if (param_2 != 1) goto LAB_0002e484;
    bVar7 = 0xfffffe0b < uVar2;
    iVar3 = uVar2 + 500;
    uVar4 = 1000;
  }
  uVar8 = __aeabi_uldivmod(iVar3,iVar5 + (uint)bVar7,uVar4,0,param_4);
LAB_0002e484:
  uVar4 = (undefined4)uVar8;
  if ((int)((ulonglong)uVar8 >> 0x20) != 0) {
    uVar4 = 0xffffffff;
  }
  return uVar4;
}


/* 0002e4a8 */

/* StopWatch::Split(StopWatch::Time*) */

void StopWatch::Split(Time *param_1)

{
  longlong lVar1;
  
  lVar1 = UtimeWrapper::GetSysCnt();
  if (lVar1 == 0) {
    lVar1 = -1;
  }
  *(longlong *)(param_1 + 8) = lVar1;
                    /* WARNING: Could not recover jumptable at 0x0001eeb0. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*(code *)PTR_GetTime_0004bdfc)(param_1,1);
  return;
}


/* 0002e4d4 */

/* UtilList::RemoveList(UtilList::_utlList*, UtilList::_utlList*) */

void UtilList::RemoveList(_utlList *param_1,_utlList *param_2)

{
  undefined4 uVar1;
  undefined4 uVar2;
  
  if (*(int *)param_1 != 0) {
    uVar1 = *(undefined4 *)(param_1 + 4);
    uVar2 = *(undefined4 *)(param_1 + 8);
    *(undefined4 *)param_2 = *(undefined4 *)param_1;
    *(undefined4 *)(param_2 + 4) = uVar1;
    *(undefined4 *)(param_2 + 8) = uVar2;
    param_2 = param_1;
  }
  (*(code *)PTR_MemSet8_0004bf78)(param_2,0,0xc);
  return;
}


/* 0002e4f8 */

/* UtilList::AddListToList(UtilList::_utlList*, UtilList::_utlList*) */

void UtilList::AddListToList(_utlList *param_1,_utlList *param_2)

{
  int iVar1;
  undefined4 uVar2;
  int *piVar3;
  undefined4 uVar4;
  
  piVar3 = *(int **)param_2;
  if (piVar3 != (int *)0x0) {
    if (*(int *)param_1 == 0) {
      uVar2 = *(undefined4 *)(param_2 + 4);
      uVar4 = *(undefined4 *)(param_2 + 8);
      *(undefined4 *)param_1 = *(undefined4 *)param_2;
      *(undefined4 *)(param_1 + 4) = uVar2;
      *(undefined4 *)(param_1 + 8) = uVar4;
      return;
    }
    iVar1 = *(int *)(param_1 + 4);
    *(int **)(iVar1 + 4) = piVar3;
    *piVar3 = iVar1;
    *(undefined4 *)(param_1 + 4) = *(undefined4 *)(param_2 + 4);
    *(int *)(param_1 + 8) = *(int *)(param_1 + 8) + *(int *)(param_2 + 8);
  }
  return;
}


/* 0002e522 */

/* UtilList::AddCellToList(UtilList::_utlList*, UtilList::_utlCell*) */

void UtilList::AddCellToList(_utlList *param_1,_utlCell *param_2)

{
  int iVar1;
  
  *(undefined4 *)(param_2 + 4) = 0;
  iVar1 = *(int *)(param_1 + 4);
  *(int *)param_2 = iVar1;
  if (iVar1 != 0) {
    *(_utlCell **)(iVar1 + 4) = param_2;
  }
  *(_utlCell **)(param_1 + 4) = param_2;
  if (*(int *)param_1 == 0) {
    *(undefined4 *)(param_1 + 8) = 0;
    *(_utlCell **)param_1 = param_2;
  }
  *(int *)(param_1 + 8) = *(int *)(param_1 + 8) + 1;
  return;
}


/* 0002e544 */

/* UtilList::AddCellToCellBefore(UtilList::_utlList*, UtilList::_utlCell*, UtilList::_utlCell*) */

void UtilList::AddCellToCellBefore(_utlList *param_1,_utlCell *param_2,_utlCell *param_3)

{
  int iVar1;
  
  *(undefined4 *)param_3 = *(undefined4 *)param_2;
  iVar1 = *(int *)param_2;
  *(_utlCell **)(param_3 + 4) = param_2;
  if (iVar1 == 0) {
    *(_utlCell **)param_1 = param_3;
  }
  else {
    *(_utlCell **)(iVar1 + 4) = param_3;
  }
  iVar1 = *(int *)(param_1 + 8);
  *(_utlCell **)param_2 = param_3;
  *(int *)(param_1 + 8) = iVar1 + 1;
  return;
}


/* 0002e562 */

/* UtilList::AddCellToCellAfter(UtilList::_utlList*, UtilList::_utlCell*, UtilList::_utlCell*) */

void UtilList::AddCellToCellAfter(_utlList *param_1,_utlCell *param_2,_utlCell *param_3)

{
  undefined4 *puVar1;
  int iVar2;
  
  *(undefined4 *)(param_3 + 4) = *(undefined4 *)(param_2 + 4);
  puVar1 = *(undefined4 **)(param_2 + 4);
  *(_utlCell **)param_3 = param_2;
  if (puVar1 == (undefined4 *)0x0) {
    *(_utlCell **)(param_1 + 4) = param_3;
  }
  else {
    *puVar1 = param_3;
  }
  iVar2 = *(int *)(param_1 + 8);
  *(_utlCell **)(param_2 + 4) = param_3;
  *(int *)(param_1 + 8) = iVar2 + 1;
  return;
}


/* 0002e580 */

/* UtilList::AddCellToListTop(UtilList::_utlList*, UtilList::_utlCell*) */

void UtilList::AddCellToListTop(_utlList *param_1,_utlCell *param_2)

{
  undefined4 *puVar1;
  
  puVar1 = *(undefined4 **)param_1;
  *(undefined4 **)(param_2 + 4) = puVar1;
  *(undefined4 *)param_2 = 0;
  if (puVar1 == (undefined4 *)0x0) {
    *(undefined4 *)(param_1 + 8) = 0;
  }
  else {
    *puVar1 = param_2;
  }
  *(_utlCell **)param_1 = param_2;
  if (*(int *)(param_1 + 4) == 0) {
    *(_utlCell **)(param_1 + 4) = param_2;
  }
  *(int *)(param_1 + 8) = *(int *)(param_1 + 8) + 1;
  return;
}


/* 0002e5a4 */

/* UtilList::InsertCellToList(UtilList::_utlList*, int, UtilList::_utlCell*) */

undefined4 UtilList::InsertCellToList(_utlList *param_1,int param_2,_utlCell *param_3)

{
  int *piVar1;
  int iVar2;
  uint uVar3;
  
  piVar1 = *(int **)param_1;
  if (piVar1 == (int *)0x0) {
    *(undefined4 *)(param_1 + 8) = 0;
  }
  uVar3 = *(uint *)(param_1 + 8);
  if ((uint)param_2 < uVar3) {
    iVar2 = 0;
    for (; piVar1 != (int *)0x0; piVar1 = (int *)piVar1[1]) {
      if (iVar2 == param_2) {
        iVar2 = *piVar1;
        *(int *)param_3 = iVar2;
        *(int **)(param_3 + 4) = piVar1;
        if (iVar2 == 0) {
          *(_utlCell **)param_1 = param_3;
        }
        else {
          *(_utlCell **)(iVar2 + 4) = param_3;
        }
        *piVar1 = (int)param_3;
        *(uint *)(param_1 + 8) = uVar3 + 1;
        return 1;
      }
      iVar2 = iVar2 + 1;
    }
  }
  AddCellToList(param_1,param_3);
  return 1;
}


/* 0002e5e6 */

/* UtilList::RemoveCellFromList(UtilList::_utlList*, UtilList::_utlCell*) */

void UtilList::RemoveCellFromList(_utlList *param_1,_utlCell *param_2)

{
  int iVar1;
  int iVar2;
  
  iVar2 = *(int *)param_2;
  iVar1 = *(int *)(param_2 + 4);
  if (iVar2 == 0) {
    if ((iVar1 == 0) && (*(_utlCell **)param_1 != param_2)) {
      return;
    }
    *(int *)param_1 = iVar1;
  }
  else {
    *(int *)(iVar2 + 4) = iVar1;
  }
  if (*(int **)(param_2 + 4) == (int *)0x0) {
    *(int *)(param_1 + 4) = iVar2;
  }
  else {
    **(int **)(param_2 + 4) = iVar2;
  }
  *(int *)(param_1 + 8) = *(int *)(param_1 + 8) + -1;
  return;
}


/* 0002e612 */

/* UtilList::SearchFromList(UtilList::_utlList*, UtilList::_utlCell*) */

undefined4 UtilList::SearchFromList(_utlList *param_1,_utlCell *param_2)

{
  _utlCell *p_Var1;
  
  p_Var1 = *(_utlCell **)param_1;
  while( true ) {
    if (p_Var1 == (_utlCell *)0x0) {
      return 0;
    }
    if (p_Var1 == param_2) break;
    p_Var1 = *(_utlCell **)(p_Var1 + 4);
  }
  return 1;
}


/* 0002e62a */

/* UtilList::GetTopCellFromList(UtilList::_utlList*) */

undefined4 UtilList::GetTopCellFromList(_utlList *param_1)

{
  return *(undefined4 *)param_1;
}


/* 0002e632 */

/* UtilList::GetTailCellFromList(UtilList::_utlList*) */

undefined4 UtilList::GetTailCellFromList(_utlList *param_1)

{
  return *(undefined4 *)(param_1 + 4);
}


/* 0002e63a */

/* UtilList::GetNextCell(UtilList::_utlCell*) */

undefined4 UtilList::GetNextCell(_utlCell *param_1)

{
  return *(undefined4 *)(param_1 + 4);
}


/* 0002e642 */

/* UtilList::GetPrevCell(UtilList::_utlCell*) */

undefined4 UtilList::GetPrevCell(_utlCell *param_1)

{
  return *(undefined4 *)param_1;
}


/* 0002e64a */

/* UtilList::GetCellCount(UtilList::_utlList*) */

undefined4 UtilList::GetCellCount(_utlList *param_1)

{
  if (*(int *)param_1 != 0) {
    return *(undefined4 *)(param_1 + 8);
  }
  return 0;
}


/* 0002e65a */

/* UtilList::GetCellPosition(UtilList::_utlList*, UtilList::_utlCell*) */

int UtilList::GetCellPosition(_utlList *param_1,_utlCell *param_2)

{
  _utlCell *p_Var1;
  int iVar2;
  
  iVar2 = 0;
  p_Var1 = (_utlCell *)GetTopCellFromList(param_1);
  while( true ) {
    if (p_Var1 == (_utlCell *)0x0) {
      return -1;
    }
    if (p_Var1 == param_2) break;
    p_Var1 = (_utlCell *)GetNextCell(p_Var1);
    iVar2 = iVar2 + 1;
  }
  return iVar2;
}


/* 0002e67e */

/* UtilStillSize::CheckStillSize(MprCtrlStill::_StillSizeTable*, DefStruct::CameraMode,
   UtilStillSize::RectSize, bool*, UtilStillSize::SizeStatus*) */

undefined4
UtilStillSize::CheckStillSize
          (int param_1,int param_2,uint param_3,undefined1 *param_4,undefined4 *param_5)

{
  uint uVar1;
  undefined4 uVar2;
  ushort *puVar3;
  uint uVar4;
  undefined4 uVar5;
  undefined1 uVar6;
  int iVar7;
  uint uVar8;
  uint uVar9;
  int local_48 [9];
  
  MemUtil::MemSet8(local_48 + 4,'\0',0x10);
  MemUtil::MemSet8(local_48,'\0',0x10);
  if (param_4 == (undefined1 *)0x0) {
    uVar2 = 0;
  }
  else if (param_5 == (undefined4 *)0x0) {
    uVar2 = 0;
  }
  else {
    *param_4 = 0;
    *param_5 = 0;
    if (param_2 == 0) {
      local_48[4] = param_2;
      local_48[0] = 0x14;
      uVar8 = 2;
      local_48[5] = 0x14;
      local_48[1] = 0x14;
    }
    else if (param_2 == 1) {
      local_48[4] = 0x28;
      local_48[0] = 8;
      uVar8 = 4;
      local_48[1] = 8;
      local_48[5] = 0x30;
      local_48[6] = 0x38;
      local_48[7] = 0x3b;
      local_48[2] = 3;
      local_48[3] = 3;
    }
    else if (param_2 == 2) {
      local_48[4] = 0x3e;
      local_48[5] = 0x3f;
      local_48[0] = 1;
      local_48[1] = 1;
      uVar8 = 2;
    }
    else if (param_2 == 3) {
      local_48[4] = 0x40;
      uVar8 = 2;
      local_48[5] = 0x4f;
      local_48[0] = 0xf;
      local_48[1] = 0xf;
    }
    else {
      if (param_2 != 4) {
        return 0;
      }
      uVar8 = 2;
      local_48[4] = 0x5e;
      local_48[5] = 0x5f;
      local_48[0] = 1;
      local_48[1] = 1;
    }
    iVar7 = 0;
    uVar1 = 0;
    do {
      uVar4 = *(uint *)((int)local_48 + iVar7 + 0x10);
      uVar9 = uVar4 + *(int *)((int)local_48 + iVar7);
      puVar3 = (ushort *)(param_1 + uVar4 * 8 + 2);
      for (; uVar4 < uVar9; uVar4 = uVar4 + 1) {
        if ((((puVar3[-1] != 0) && (*puVar3 != 0)) && ((param_3 & 0xffff) == (uint)puVar3[-1])) &&
           (param_3 >> 0x10 == (uint)*puVar3)) {
          uVar6 = 1;
          uVar5 = 0;
          goto LAB_0002e7dc;
        }
        puVar3 = puVar3 + 4;
      }
      uVar1 = uVar1 + 1;
      iVar7 = iVar7 + 4;
    } while (uVar1 < uVar8);
    iVar7 = 0;
    uVar1 = 0;
    do {
      uVar4 = *(uint *)((int)local_48 + iVar7 + 0x10);
      uVar9 = uVar4 + *(int *)((int)local_48 + iVar7);
      puVar3 = (ushort *)(param_1 + uVar4 * 8 + 2);
      for (; uVar4 < uVar9; uVar4 = uVar4 + 1) {
        if (((puVar3[-1] != 0) && (*puVar3 != 0)) &&
           (((param_3 & 0xffff) <= (uint)puVar3[-1] && (param_3 >> 0x10 <= (uint)*puVar3)))) {
          uVar6 = 0;
          uVar5 = 0;
          goto LAB_0002e7dc;
        }
        puVar3 = puVar3 + 4;
      }
      uVar1 = uVar1 + 1;
      iVar7 = iVar7 + 4;
    } while (uVar1 < uVar8);
    uVar6 = 0;
    uVar5 = 1;
LAB_0002e7dc:
    *param_4 = uVar6;
    uVar2 = 1;
    *param_5 = uVar5;
  }
  return uVar2;
}


/* 0002e7f4 */

/* UtilStillSize::GetStillTargetFileSize(int, DefStruct::StillSize, DefStruct::StillAspect,
   DefStruct::JpgQuality, DefStruct::CropType, bool) */

int UtilStillSize::GetStillTargetFileSize
              (int param_1,int param_2,int param_3,int param_4,int param_5,char param_6)

{
  int iVar1;
  int local_38;
  int local_34;
  int local_30;
  MonCtrl aMStack_2c [16];
  
  MonCtrl::MonCtrl(aMStack_2c,(char *)(DAT_0002e8a8 + 0x2e810),true);
  if (param_6 != '\0') {
    MonCtrl::ConPrintfMessage((char *)aMStack_2c,DAT_0002e8ac + 0x2e82a,param_2,param_3,param_4);
  }
  if (param_1 == 3) {
    iVar1 = 1;
  }
  else {
    iVar1 = 0xff;
  }
  iVar1 = MprCtrl::GetStillDataInfo
                    (param_1,param_2,param_3,param_4,param_5,iVar1,(StillDataInfo *)&local_38);
  if (iVar1 < 0) {
    MonCtrl::ConPrintfMessage((char *)aMStack_2c,DAT_0002e8b0 + 0x2e860,0x15e);
    iVar1 = 0;
  }
  else {
    iVar1 = 0;
    if (local_38 != 0) {
      iVar1 = local_38 + local_34 + local_30;
    }
  }
  if (param_6 != '\0') {
    MonCtrl::ConPrintfMessage((char *)aMStack_2c,DAT_0002e8b4 + 0x2e886,iVar1);
  }
  MonCtrl::~MonCtrl(aMStack_2c);
  return iVar1;
}


/* 0002e8b8 */

/* UtilStillSize::GetContentAspect(UtilStillSize::RectSize) */

undefined4 UtilStillSize::GetContentAspect(uint param_1)

{
  ushort uVar1;
  undefined4 uVar2;
  short extraout_r1;
  short extraout_r1_00;
  short extraout_r1_01;
  uint uVar3;
  uint uVar4;
  
  uVar3 = param_1 >> 0x10;
  uVar4 = param_1 & 0xffff;
  uVar1 = __aeabi_uidiv(uVar3,9);
  if (((uVar4 >> 4 == (uint)uVar1) && ((param_1 & 0xf) == 0)) &&
     (__aeabi_uidivmod(uVar3,9), extraout_r1 == 0)) {
    uVar2 = 1;
  }
  else {
    uVar1 = __aeabi_uidiv(uVar3,3);
    if (((uVar4 >> 2 == (uint)uVar1) && ((param_1 & 3) == 0)) &&
       (__aeabi_uidivmod(uVar3,3), extraout_r1_00 == 0)) {
      return 0;
    }
    uVar1 = __aeabi_uidiv(uVar4,3);
    if ((((uint)uVar1 == param_1 >> 0x11) && (__aeabi_uidivmod(uVar4,3), extraout_r1_01 == 0)) &&
       ((uVar3 & 1) == 0)) {
      uVar2 = 2;
    }
    else if (uVar4 == 0xcc0) {
      if (uVar3 == 0x730) {
        uVar2 = 1;
      }
      else {
        uVar2 = 0xffffffff;
      }
    }
    else {
      if (uVar4 == 0xe40) {
        uVar4 = 0x808;
      }
      else {
        if (uVar4 != 4000) {
          if (uVar4 != 0x10e0) {
            return 0xffffffff;
          }
          if (uVar3 != 0x980) {
            return 0xffffffff;
          }
          return 1;
        }
        uVar4 = 0x8c8;
      }
      if (uVar3 == uVar4) {
        uVar2 = 1;
      }
      else {
        uVar2 = 0xffffffff;
      }
    }
  }
  return uVar2;
}


/* 0002e98c */

/* UtilStillSize::IsRecordingSCN(UtilStillSize::RectSize) */

bool UtilStillSize::IsRecordingSCN(uint param_1)

{
  int iVar1;
  
  iVar1 = (param_1 & 0xffff) * (param_1 >> 0x10);
  return iVar1 - DAT_0002e9ac != 0 && DAT_0002e9ac <= iVar1;
}


/* 0002e9b0 */

/* UtilStillSize::CnvStillSize(int) */

undefined4 UtilStillSize::CnvStillSize(int param_1)

{
  if ((uint)param_1 < 4) {
    return *(undefined4 *)(DAT_0002e9c8 + 0x2e9be + param_1 * 4);
  }
  return 0;
}


/* 0002e9cc */

/* UtilStillSize::CnvStillAspect(int) */

undefined4 UtilStillSize::CnvStillAspect(int param_1)

{
  if ((uint)param_1 < 5) {
    return *(undefined4 *)(DAT_0002e9e4 + 0x2e9da + param_1 * 4);
  }
  return 2;
}


/* 0002e9e8 */

/* UtilStillSize::CnvDualRecSize(int) */

undefined4 UtilStillSize::CnvDualRecSize(int param_1)

{
  if ((uint)param_1 < 4) {
    return *(undefined4 *)(DAT_0002ea00 + 0x2e9f6 + param_1 * 4);
  }
  return 0;
}


/* 0002ea04 */

/* UtilStillSize::CnvMovieAspect(int) */

undefined4 UtilStillSize::CnvMovieAspect(int param_1)

{
  if ((uint)param_1 < 5) {
    return *(undefined4 *)(DAT_0002ea1c + 0x2ea12 + param_1 * 4);
  }
  return 1;
}


/* 0002ea20 */

/* UtilStillSize::CnvPbCapSize(int) */

undefined4 UtilStillSize::CnvPbCapSize(int param_1)

{
  if ((uint)param_1 < 3) {
    return *(undefined4 *)(DAT_0002ea38 + 0x2ea2e + param_1 * 4);
  }
  return 0;
}


/* 0002ea3c */

/* UtilStillSize::CalcScnOption(UtilStillSize::RectSize, int) */

undefined4 UtilStillSize::CalcScnOption(undefined4 param_1,uint param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = IsRecordingSCN();
  if ((iVar1 == 0) || (4 < param_2)) {
    uVar2 = 0xff;
  }
  else {
    uVar2 = *(undefined4 *)(DAT_0002ea64 + 0x2ea56 + param_2 * 4);
  }
  return uVar2;
}


/* 0002ea68 */

/* UtilStillSize::SearchApproxStillSize(MprCtrlStill::_StillSizeTable*, UtilStillSize::RectSize,
   int*, int*, int*, int*, int*) */

void UtilStillSize::SearchApproxStillSize
               (ushort *param_1,uint param_2,undefined4 *param_3,undefined4 *param_4,
               undefined4 *param_5,undefined4 *param_6,undefined4 *param_7)

{
  int iVar1;
  undefined4 uVar2;
  int extraout_r1;
  int extraout_r1_00;
  int extraout_r1_01;
  int extraout_r1_02;
  uint uVar3;
  ushort *puVar4;
  uint uVar5;
  int iVar6;
  uint uVar7;
  
  uVar5 = (param_2 & 0xffff) * (param_2 >> 0x10);
  uVar3 = uVar5;
  iVar1 = 0;
  puVar4 = param_1;
  do {
    iVar6 = iVar1;
    uVar7 = (uint)*puVar4 * (uint)puVar4[1];
    if (uVar5 < uVar7) {
      uVar7 = uVar7 - uVar5;
    }
    else {
      uVar7 = uVar5 - uVar7;
    }
    if ((uVar7 < uVar3) || (iVar6 == 0)) {
      *param_6 = 0;
      *param_3 = 2;
      iVar1 = __aeabi_uidiv(iVar6,5);
      uVar2 = CnvStillSize(iVar1);
      *param_4 = uVar2;
      __aeabi_uidivmod(iVar6,5);
      uVar2 = CnvStillAspect(extraout_r1);
      *param_5 = uVar2;
      uVar2 = CalcScnOption(param_2,uVar2);
      *param_7 = uVar2;
      uVar3 = uVar7;
    }
    puVar4 = puVar4 + 4;
    iVar1 = iVar6 + 1;
  } while (iVar6 + 1 != 0x14);
  iVar1 = iVar6 + -0x13;
  puVar4 = param_1;
  do {
    iVar6 = iVar1;
    uVar7 = (uint)puVar4[0x50] * (uint)puVar4[0x51];
    if (uVar5 < uVar7) {
      uVar7 = uVar7 - uVar5;
    }
    else {
      uVar7 = uVar5 - uVar7;
    }
    if (uVar7 < uVar3) {
      *param_6 = 1;
      *param_3 = 2;
      iVar1 = __aeabi_uidiv(iVar6,5);
      uVar2 = CnvStillSize(iVar1);
      *param_4 = uVar2;
      __aeabi_uidivmod(iVar6,5);
      uVar2 = CnvStillAspect(extraout_r1_00);
      *param_5 = uVar2;
      uVar2 = CalcScnOption(param_2,uVar2);
      *param_7 = uVar2;
      uVar3 = uVar7;
    }
    puVar4 = puVar4 + 4;
    iVar1 = iVar6 + 1;
  } while (iVar6 + 1 != 0x14);
  iVar6 = iVar6 + -0x13;
  puVar4 = param_1;
  do {
    uVar7 = (uint)puVar4[0x100] * (uint)puVar4[0x101];
    if (uVar5 < uVar7) {
      uVar7 = uVar7 - uVar5;
    }
    else {
      uVar7 = uVar5 - uVar7;
    }
    if (uVar7 < uVar3) {
      *param_6 = 0;
      *param_3 = 0;
      iVar1 = __aeabi_uidiv(iVar6,5);
      uVar2 = CnvDualRecSize(iVar1);
      *param_4 = uVar2;
      __aeabi_uidivmod(iVar6,5);
      uVar2 = CnvMovieAspect(extraout_r1_01);
      *param_5 = uVar2;
      uVar2 = CalcScnOption(param_2,uVar2);
      *param_7 = uVar2;
      uVar3 = uVar7;
    }
    iVar6 = iVar6 + 1;
    puVar4 = puVar4 + 4;
  } while (iVar6 != 0x14);
  iVar1 = 0;
  do {
    uVar7 = (uint)param_1[0x13c] * (uint)param_1[0x13d];
    if (uVar5 < uVar7) {
      uVar7 = uVar7 - uVar5;
    }
    else {
      uVar7 = uVar5 - uVar7;
    }
    if (uVar7 < uVar3) {
      *param_6 = 1;
      *param_3 = 0;
      iVar6 = __aeabi_uidiv(iVar1,5);
      uVar2 = CnvDualRecSize(iVar6);
      *param_4 = uVar2;
      __aeabi_uidivmod(iVar1,5);
      uVar2 = CnvMovieAspect(extraout_r1_02);
      *param_5 = uVar2;
      uVar2 = CalcScnOption(param_2,uVar2);
      *param_7 = uVar2;
      uVar3 = uVar7;
    }
    iVar1 = iVar1 + 1;
    param_1 = param_1 + 4;
  } while (iVar1 != 0x14);
  return;
}


/* 0002ec44 */

/* UtilStillSize::SearchStillSize(MprCtrlStill::_StillSizeTable*, UtilStillSize::RectSize, int*,
   int*, int*, int*, int*) */

undefined4
UtilStillSize::SearchStillSize
          (int param_1,uint param_2,undefined4 *param_3,undefined4 *param_4,undefined4 *param_5,
          undefined4 *param_6,undefined4 *param_7)

{
  undefined4 uVar1;
  int iVar2;
  uint uVar3;
  int extraout_r1;
  int extraout_r1_00;
  int extraout_r1_01;
  int extraout_r1_02;
  int iVar4;
  int iVar5;
  uint uVar6;
  
  uVar6 = param_2 & 0xffff;
  uVar3 = param_2 >> 0x10;
  iVar5 = 0x60;
  iVar4 = param_1;
  do {
    iVar2 = iVar5;
    if ((*(ushort *)(iVar4 + 0x300) == uVar6) && (*(ushort *)(iVar4 + 0x302) == uVar3)) {
      *param_6 = 0;
      *param_3 = 1;
      uVar1 = CnvPbCapSize(iVar2 + -0x60);
      *param_4 = uVar1;
      uVar1 = *param_5;
      goto LAB_0002edb2;
    }
    iVar4 = iVar4 + 8;
    iVar5 = iVar2 + 1;
  } while (iVar2 + 1 != 99);
  iVar2 = iVar2 + -0x62;
  iVar5 = iVar2;
  do {
    if ((*(ushort *)(param_1 + iVar2) == uVar6) && (*(ushort *)(param_1 + iVar2 + 2) == uVar3)) {
      *param_6 = 0;
      *param_3 = 2;
      iVar4 = __aeabi_uidiv(iVar5,5);
      uVar1 = CnvStillSize(iVar4);
      *param_4 = uVar1;
      __aeabi_uidivmod(iVar5,5);
      uVar1 = CnvStillAspect(extraout_r1);
      goto LAB_0002ed5a;
    }
    iVar5 = iVar5 + 1;
    iVar2 = iVar2 + 8;
  } while (iVar5 != 0x14);
  iVar5 = param_1;
  iVar4 = 0x14;
  while ((iVar2 = iVar4, *(ushort *)(iVar5 + 0xa0) != uVar6 || (*(ushort *)(iVar5 + 0xa2) != uVar3))
        ) {
    iVar5 = iVar5 + 8;
    iVar4 = iVar2 + 1;
    if (iVar2 + 1 == 0x28) {
      iVar2 = iVar2 + 0x19;
      iVar5 = param_1;
      do {
        if ((*(ushort *)(iVar5 + 0x200) == uVar6) && (*(ushort *)(iVar5 + 0x202) == uVar3)) {
          *param_6 = 0;
          *param_3 = 0;
          iVar5 = __aeabi_uidiv(iVar2 + -0x40,5);
          uVar1 = CnvDualRecSize(iVar5);
          *param_4 = uVar1;
          __aeabi_uidivmod(iVar2 + -0x40,5);
          uVar1 = CnvMovieAspect(extraout_r1_01);
LAB_0002ed5a:
          *param_5 = uVar1;
          uVar1 = CalcScnOption(param_2,uVar1);
          *param_7 = uVar1;
          return 1;
        }
        iVar2 = iVar2 + 1;
        iVar5 = iVar5 + 8;
      } while (iVar2 != 0x4f);
      while ((*(ushort *)(param_1 + 0x278) != uVar6 || (*(ushort *)(param_1 + 0x27a) != uVar3))) {
        iVar2 = iVar2 + 1;
        param_1 = param_1 + 8;
        if (iVar2 == 0x5e) {
          return 0;
        }
      }
      *param_6 = 1;
      *param_3 = 0;
      iVar5 = __aeabi_uidiv(iVar2 + -0x4f,5);
      uVar1 = CnvDualRecSize(iVar5);
      *param_4 = uVar1;
      __aeabi_uidivmod(iVar2 + -0x4f,5);
      uVar1 = CnvMovieAspect(extraout_r1_02);
LAB_0002edac:
      *param_5 = uVar1;
LAB_0002edb2:
      uVar1 = CalcScnOption(param_2,uVar1);
      *param_7 = uVar1;
      return 1;
    }
  }
  *param_6 = 1;
  *param_3 = 2;
  iVar5 = __aeabi_uidiv(iVar2 + -0x14,5);
  uVar1 = CnvStillSize(iVar5);
  *param_4 = uVar1;
  __aeabi_uidivmod(iVar2 + -0x14,5);
  uVar1 = CnvStillAspect(extraout_r1_00);
  goto LAB_0002edac;
}


/* 0002edd4 */

/* UtilStillSize::GetStillTargetSize(bool, UtilStillSize::RectSize, DefStruct::JpgQuality, int*,
   int*, int*, bool) */

bool UtilStillSize::GetStillTargetSize
               (undefined4 param_1,undefined4 param_2,int param_3,undefined4 *param_4,
               undefined4 *param_5,undefined4 *param_6,char param_7)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  bool bVar4;
  undefined4 local_4c;
  undefined4 local_48;
  undefined4 local_44;
  MonCtrl aMStack_40 [12];
  int local_34;
  int local_30;
  int local_2c;
  int local_28;
  int local_24;
  
  local_24 = 2;
  local_28 = 2;
  local_2c = 2;
  local_30 = 0;
  local_34 = 0xff;
  MonCtrl::MonCtrl(aMStack_40,(char *)(DAT_0002efa0 + 0x2edf2),true);
  if (((param_4 == (undefined4 *)0x0) || (param_5 == (undefined4 *)0x0)) ||
     (param_6 == (undefined4 *)0x0)) {
    uVar3 = 0xcc;
    iVar2 = DAT_0002efa4 + 0x2ee26;
  }
  else {
    *param_4 = 0;
    *param_5 = 0;
    *param_6 = 0;
    iVar2 = MprCtrl::GetStillSizeTable();
    if (iVar2 != 0) {
      iVar1 = SearchStillSize(iVar2,param_2,&local_24,&local_28,&local_2c,&local_30,&local_34);
      if (iVar1 == 0) {
        if (param_7 != '\0') {
          MonCtrl::ConPrintfMessage((char *)aMStack_40,DAT_0002efb0 + 0x2ee8c,local_24);
        }
        SearchApproxStillSize(iVar2,param_2,&local_24,&local_28,&local_2c,&local_30,&local_34);
        if (param_7 != '\0') goto LAB_0002eeb2;
      }
      else if (param_7 != '\0') {
        MonCtrl::ConPrintfMessage((char *)aMStack_40,DAT_0002efac + 0x2ee7a,local_24);
LAB_0002eeb2:
        MonCtrl::ConPrintfMessage((char *)aMStack_40,DAT_0002efb4 + 0x2eebe,local_24);
        MonCtrl::ConPrintfMessage((char *)aMStack_40,DAT_0002efb8 + 0x2eecc,local_28);
        MonCtrl::ConPrintfMessage((char *)aMStack_40,DAT_0002efbc + 0x2eeda,local_2c);
        MonCtrl::ConPrintfMessage((char *)aMStack_40,DAT_0002efc0 + 0x2eee8,local_30);
        MonCtrl::ConPrintfMessage((char *)aMStack_40,DAT_0002efc4 + 0x2eef6,local_34);
      }
      iVar2 = MprCtrl::GetStillDataInfo
                        (local_24,local_28,local_2c,param_3,local_30,local_34,
                         (StillDataInfo *)&local_4c);
      bVar4 = -1 < iVar2;
      if (bVar4) {
        *param_4 = local_4c;
        *param_5 = local_48;
        *param_6 = local_44;
      }
      else {
        MonCtrl::ConPrintfMessage((char *)aMStack_40,DAT_0002efc8 + 0x2ef24,0x11b);
      }
      if (param_7 != '\0') {
        MonCtrl::ConPrintfMessage((char *)aMStack_40,DAT_0002efcc + 0x2ef4a);
        MonCtrl::ConPrintfMessage((char *)aMStack_40,DAT_0002efd0 + 0x2ef58,*param_4);
        MonCtrl::ConPrintfMessage((char *)aMStack_40,DAT_0002efd4 + 0x2ef68,*param_5);
        MonCtrl::ConPrintfMessage((char *)aMStack_40,DAT_0002efd8 + 0x2ef78,*param_6);
      }
      goto LAB_0002ef7e;
    }
    uVar3 = 0xda;
    iVar2 = DAT_0002efa8 + 0x2ee44;
  }
  MonCtrl::ConPrintfMessage((char *)aMStack_40,iVar2,uVar3);
  bVar4 = false;
LAB_0002ef7e:
  MonCtrl::~MonCtrl(aMStack_40);
  return bVar4;
}


/* 0002efdc */

/* Version::PrintVersion(unsigned int) */

void Version::PrintVersion(uint param_1)

{
  int iVar1;
  uint uVar2;
  MonCtrl aMStack_1c [12];
  
  MonCtrl::MonCtrl(aMStack_1c,(char *)(DAT_0002f078 + 0x2efea),true);
  iVar1 = 0;
  uVar2 = 0;
  do {
    if (param_1 == *(uint *)(DAT_0002f07c + 0x2effa + iVar1)) {
      MonCtrl::ConPutStr((char *)aMStack_1c);
      MonCtrl::ConPutStr((char *)aMStack_1c);
      MonCtrl::ConPutStr((char *)aMStack_1c);
      MonCtrl::ConPutStr((char *)aMStack_1c);
      MonCtrl::ConPutStr((char *)aMStack_1c);
      MonCtrl::ConPutCRLF();
      if (uVar2 < 0x11) goto LAB_0002f060;
      break;
    }
    uVar2 = uVar2 + 1;
    iVar1 = iVar1 + 0xc;
  } while (uVar2 != 0x11);
  MonCtrl::ConPutStr((char *)aMStack_1c);
LAB_0002f060:
  MonCtrl::~MonCtrl(aMStack_1c);
  return;
}


/* 0002f098 */

/* CapIdWrapper::Mmap(CapIdWrapper::MemExtent*, int*, CapIdWrapper::MemExtent*) */

undefined4 __thiscall
CapIdWrapper::Mmap(CapIdWrapper *this,MemExtent *param_1,int *param_2,MemExtent *param_3)

{
  int iVar1;
  void *pvVar2;
  undefined4 uVar3;
  
  iVar1 = DAT_0002f104;
  *param_2 = -1;
  *(undefined4 *)param_3 = 0;
  *(undefined4 *)(param_3 + 4) = 0;
  iVar1 = open((char *)(iVar1 + 0x2f0b8),0x1002);
  if (iVar1 != -1) {
    pvVar2 = mmap((void *)0x0,*(size_t *)(param_1 + 4),3,1,iVar1,*(__off_t *)param_1);
    if (pvVar2 != (void *)0xffffffff) {
      *param_2 = iVar1;
      uVar3 = *(undefined4 *)(param_1 + 4);
      *(void **)param_3 = pvVar2;
      *(undefined4 *)(param_3 + 4) = uVar3;
      return 0;
    }
    close(iVar1);
  }
  return 6;
}


/* 0002f108 */

/* CapIdWrapper::SendCapIdTblCommand(unsigned int) */

int __thiscall CapIdWrapper::SendCapIdTblCommand(CapIdWrapper *this,uint param_1)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  undefined4 local_3c;
  uint local_38;
  int local_24 [2];
  int *local_1c [2];
  
  local_1c[0] = (int *)0x0;
  MemUtil::MemSet8(&local_3c,'\0',0x18);
  local_24[0] = 0;
  local_24[1] = 0;
  local_3c = 0;
  local_38 = param_1;
  iVar2 = osal_valloc_msg_wait(DAT_0002f1d4,local_1c,0x18,1);
  if (iVar2 == 0) {
    MemUtil::MemCpy8(local_1c[0],&local_3c,0x18);
    uVar1 = DAT_0002f1d4;
    local_1c[0][-1] = *(int *)(this + 0x14);
    iVar2 = osal_snd_msg(uVar1);
    if ((((iVar2 == 0) &&
         (iVar3 = osal_rcv_msg_tmo(*(undefined4 *)(this + 0x14),local_1c,0xffffffff), iVar2 = iVar3,
         iVar3 == 0)) && (uVar5 = local_1c[0][1], iVar2 = DAT_0002f1d8, uVar5 == param_1)) &&
       (*local_1c[0] == 1)) {
      if (local_1c[0][2] == 0) {
        if (uVar5 == 0x1000) {
          local_24[0] = local_1c[0][3];
          local_24[1] = 0xc40;
          iVar4 = Mmap(this,(MemExtent *)local_24,(int *)(this + 8),(MemExtent *)(this + 0xc));
          iVar2 = DAT_0002f1dc;
          if (iVar4 == 0) {
            *(undefined4 *)(this + 4) = *(undefined4 *)(this + 0xc);
            iVar2 = iVar3;
          }
        }
        else if ((0xfff < uVar5) && (uVar5 < 0x1003)) {
          iVar2 = iVar3;
        }
      }
      else {
        iVar2 = -0x3fd;
      }
    }
    osal_free_msg(*(undefined4 *)(this + 0x14),local_1c[0]);
  }
  return iVar2;
}


/* 0002f1e0 */

/* CapIdWrapper::UnlockRelease() */

undefined4 __thiscall CapIdWrapper::UnlockRelease(CapIdWrapper *this)

{
  int iVar1;
  undefined4 uVar2;
  
  if (this[0x18] == (CapIdWrapper)0x0) {
    return 4;
  }
  if (*(int *)(this + 4) != 0) {
    iVar1 = SendCapIdTblCommand(this,0x1001);
    if (iVar1 != 0) {
      return 0xffff;
    }
    *(undefined4 *)(*(int *)(this + 4) + 0x3c) = 0;
    iVar1 = SendCapIdTblCommand(this,0x1002);
    if (iVar1 == 0) {
      uVar2 = 0;
    }
    else {
      uVar2 = 0xffff;
    }
    return uVar2;
  }
  return 2;
}


/* 0002f228 */

/* CapIdWrapper::LockRelease() */

undefined4 __thiscall CapIdWrapper::LockRelease(CapIdWrapper *this)

{
  int iVar1;
  undefined4 uVar2;
  
  if (this[0x18] == (CapIdWrapper)0x0) {
    return 4;
  }
  if (*(int *)(this + 4) != 0) {
    iVar1 = SendCapIdTblCommand(this,0x1001);
    if (iVar1 != 0) {
      return 0xffff;
    }
    *(undefined4 *)(*(int *)(this + 4) + 0x3c) = 1;
    iVar1 = SendCapIdTblCommand(this,0x1002);
    if (iVar1 == 0) {
      uVar2 = 0;
    }
    else {
      uVar2 = 0xffff;
    }
    return uVar2;
  }
  return 2;
}


/* 0002f272 */

/* CapIdWrapper::IsReleaseLocked(bool*) */

undefined4 __thiscall CapIdWrapper::IsReleaseLocked(CapIdWrapper *this,bool *param_1)

{
  int iVar1;
  undefined4 uVar2;
  bool bVar3;
  
  *param_1 = false;
  if (this[0x18] == (CapIdWrapper)0x0) {
    return 4;
  }
  if (*(int *)(this + 4) != 0) {
    iVar1 = SendCapIdTblCommand(this,0x1001);
    if (iVar1 != 0) {
      return 0xffff;
    }
    bVar3 = true;
    if (*(int *)(*(int *)(this + 4) + 0x3c) != 1) {
      bVar3 = *param_1;
    }
    *param_1 = bVar3;
    iVar1 = SendCapIdTblCommand(this,0x1002);
    if (iVar1 == 0) {
      uVar2 = 0;
    }
    else {
      uVar2 = 0xffff;
    }
    return uVar2;
  }
  return 2;
}


/* 0002f2c8 */

/* CapIdWrapper::ReadCapIdRow(CapIdWrapper::CaptureIdRow*) */

undefined4 __thiscall CapIdWrapper::ReadCapIdRow(CapIdWrapper *this,CaptureIdRow *param_1)

{
  int iVar1;
  uint uVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  
  MemUtil::MemSet8(param_1,'\0',0xc);
  if (this[0x18] == (CapIdWrapper)0x0) {
    uVar4 = 4;
  }
  else if (*(int *)(this + 4) == 0) {
    uVar4 = 2;
  }
  else {
    iVar1 = SendCapIdTblCommand(this,0x1001);
    if (iVar1 == 0) {
      iVar1 = *(int *)(this + 4);
      if ((*(int *)(iVar1 + 0x3c) == 1) || (*(int *)(iVar1 + 8) == *(int *)(iVar1 + 4))) {
        uVar4 = 0x9000;
      }
      else {
        uVar2 = *(int *)(iVar1 + 4) + 1U & 0xff;
        *(uint *)(iVar1 + 4) = uVar2;
        iVar1 = uVar2 * 0xc + iVar1;
        uVar4 = *(undefined4 *)(iVar1 + 0x44);
        uVar3 = *(undefined4 *)(iVar1 + 0x48);
        *(undefined4 *)param_1 = *(undefined4 *)(iVar1 + 0x40);
        *(undefined4 *)(param_1 + 4) = uVar4;
        *(undefined4 *)(param_1 + 8) = uVar3;
        uVar4 = 0;
      }
      iVar1 = SendCapIdTblCommand(this,0x1002);
      if (iVar1 != 0) {
        uVar4 = 0xffff;
      }
    }
    else {
      uVar4 = 0xffff;
    }
  }
  return uVar4;
}


/* 0002f34a */

/* CapIdWrapper::CheckReadStatus(unsigned int*) */

undefined4 __thiscall CapIdWrapper::CheckReadStatus(CapIdWrapper *this,uint *param_1)

{
  CapIdWrapper CVar1;
  int iVar2;
  undefined4 uVar3;
  
  CVar1 = this[0x18];
  *param_1 = 1;
  if (CVar1 == (CapIdWrapper)0x0) {
    return 4;
  }
  if (*(int *)(this + 4) != 0) {
    *param_1 = 0;
    iVar2 = SendCapIdTblCommand(this,0x1001);
    if (iVar2 != 0) {
      return 0xffff;
    }
    iVar2 = *(int *)(this + 4);
    if (*(int *)(iVar2 + 0x3c) == 1) {
      *param_1 = 2;
    }
    else if (*(int *)(iVar2 + 8) == *(int *)(iVar2 + 4)) {
      *param_1 = 1;
    }
    iVar2 = SendCapIdTblCommand(this,0x1002);
    if (iVar2 == 0) {
      uVar3 = 0;
    }
    else {
      uVar3 = 0xffff;
    }
    return uVar3;
  }
  return 2;
}


/* 0002f3b0 */

/* CapIdWrapper::InitCapIdTbl(unsigned int, unsigned int, unsigned int) */

undefined4 __thiscall
CapIdWrapper::InitCapIdTbl(CapIdWrapper *this,uint param_1,uint param_2,uint param_3)

{
  int iVar1;
  undefined4 uVar2;
  
  if (this[0x18] == (CapIdWrapper)0x0) {
    return 4;
  }
  if (*(int *)(this + 4) != 0) {
    iVar1 = SendCapIdTblCommand(this,0x1001);
    if (iVar1 != 0) {
      return 0xffff;
    }
    iVar1 = *(int *)(this + 4);
    *(uint *)(iVar1 + 4) = param_1;
    *(uint *)(iVar1 + 8) = param_2;
    *(uint *)(iVar1 + 0xc) = param_3;
    MemUtil::MemSet8((void *)(iVar1 + 0x10),'\0',0x1c);
    memset((void *)(*(int *)(this + 4) + 0x40),0,0xc00);
    iVar1 = SendCapIdTblCommand(this,0x1002);
    if (iVar1 == 0) {
      uVar2 = 0;
    }
    else {
      uVar2 = 0xffff;
    }
    return uVar2;
  }
  return 2;
}


/* 0002f42c */

/* CapIdWrapper::CapIdWrapper(unsigned short) */

CapIdWrapper * __thiscall CapIdWrapper::CapIdWrapper(CapIdWrapper *this,ushort param_1)

{
  int iVar1;
  
  *(int *)this = *(int *)(DAT_0002f470 + 0x2f434 + DAT_0002f474) + 8;
  *(undefined4 *)(this + 4) = 0;
  MemUtil::MemSet8(this + 8,'\0',0xc);
  iVar1 = MprCtrl::IsCaptureIdTable();
  this[0x18] = SUB41(iVar1,0);
  if (iVar1 != 0) {
    osal_dynamic_id(0x2a,param_1,this + 0x14);
    SendCapIdTblCommand(this,0x1000);
  }
  return this;
}


/* 0002f478 */

/* CapIdWrapper::Munmap(int, CapIdWrapper::MemExtent*) */

undefined4 __thiscall CapIdWrapper::Munmap(CapIdWrapper *this,int param_1,MemExtent *param_2)

{
  if (*(void **)param_2 != (void *)0x0) {
    munmap(*(void **)param_2,*(size_t *)(param_2 + 4));
  }
  if (param_1 != -1) {
    close(param_1);
  }
  return 0;
}


/* 0002f498 */

/* CapIdWrapper::~CapIdWrapper() */

CapIdWrapper * __thiscall CapIdWrapper::~CapIdWrapper(CapIdWrapper *this)

{
  *(int *)this = *(int *)(DAT_0002f4c8 + 0x2f4a6 + DAT_0002f4cc) + 8;
  if (this[0x18] != (CapIdWrapper)0x0) {
    osal_dynamic_id(0x4a,0,*(undefined4 *)(this + 0x14));
    Munmap(this,*(int *)(this + 8),(MemExtent *)(this + 0xc));
  }
  return this;
}


/* 0002f4d0 */

/* CapIdWrapper::~CapIdWrapper() */

CapIdWrapper * __thiscall CapIdWrapper::~CapIdWrapper(CapIdWrapper *this)

{
  ~CapIdWrapper(this);
  operator_delete(this);
  return this;
}


/* 0002f4e4 */

/* ConnectPinWrapper::~ConnectPinWrapper() */

ConnectPinWrapper * __thiscall ConnectPinWrapper::~ConnectPinWrapper(ConnectPinWrapper *this)

{
  *(int *)this = *(int *)(DAT_0002f504 + 0x2f4f2 + DAT_0002f508) + 8;
  if (*(int **)(this + 8) != (int *)0x0) {
    (**(code **)(**(int **)(this + 8) + 4))();
  }
  return this;
}


/* 0002f50c */

/* ConnectPinWrapper::~ConnectPinWrapper() */

ConnectPinWrapper * __thiscall ConnectPinWrapper::~ConnectPinWrapper(ConnectPinWrapper *this)

{
  ~ConnectPinWrapper(this);
  operator_delete(this);
  return this;
}


/* 0002f520 */

/* ConnectPinWrapper::ConnectPinWrapper(MWF::ObjPin*) */

ConnectPinWrapper * __thiscall
ConnectPinWrapper::ConnectPinWrapper(ConnectPinWrapper *this,ObjPin *param_1)

{
  ObjLock *this_00;
  int iVar1;
  
  iVar1 = *(int *)(DAT_0002f55c + 0x2f528 + DAT_0002f560);
  *(ObjPin **)(this + 4) = param_1;
  *(int *)this = iVar1 + 8;
  *(undefined4 *)(this + 0xc) = 0;
  *(undefined4 *)(this + 0x10) = 0;
  this[0x14] = (ConnectPinWrapper)0x0;
  this[0x15] = (ConnectPinWrapper)0x0;
  this[0x16] = (ConnectPinWrapper)0x0;
  this_00 = operator_new(0x1c);
  MWF::ObjLock::ObjLock(this_00);
  *(ObjLock **)(this + 8) = this_00;
  return this;
}


/* 0002f564 */

/* ConnectPinWrapper::Connect(MWF::ObjPin*, MWF::ObjStatusViewer*) */

void __thiscall
ConnectPinWrapper::Connect(ConnectPinWrapper *this,ObjPin *param_1,ObjStatusViewer *param_2)

{
  MWF::ObjLock::Lock(*(ObjLock **)(this + 8));
  if (this[0x15] == (ConnectPinWrapper)0x0) {
    MWF::ObjPin::Connect(*(ObjPin **)(this + 4),(ObjStatusViewer *)param_1);
  }
  else {
    this[0x16] = (ConnectPinWrapper)0x1;
  }
  *(ObjPin **)(this + 0xc) = param_1;
  *(ObjStatusViewer **)(this + 0x10) = param_2;
  (*(code *)PTR_Unlock_0004c134)(*(undefined4 *)(this + 8));
  return;
}


/* 0002f598 */

/* ConnectPinWrapper::Disconnect() */

void __thiscall ConnectPinWrapper::Disconnect(ConnectPinWrapper *this)

{
  MWF::ObjLock::Lock(*(ObjLock **)(this + 8));
  if (this[0x14] == (ConnectPinWrapper)0x0) {
    MWF::ObjPin::Disconnect();
  }
  else {
    this[0x15] = (ConnectPinWrapper)0x1;
  }
  (*(code *)PTR_Unlock_0004c134)(*(undefined4 *)(this + 8));
  return;
}


/* 0002f5be */

/* ConnectPinWrapper::SetStatus(bool) */

void __thiscall ConnectPinWrapper::SetStatus(ConnectPinWrapper *this,bool param_1)

{
  ConnectPinWrapper CVar1;
  
  MWF::ObjLock::Lock(*(ObjLock **)(this + 8));
  if (param_1) {
    CVar1 = (ConnectPinWrapper)0x1;
  }
  else {
    if (this[0x15] != (ConnectPinWrapper)0x0) {
      MWF::ObjPin::Disconnect();
      this[0x15] = (ConnectPinWrapper)param_1;
      if (this[0x16] != (ConnectPinWrapper)0x0) {
        MWF::ObjPin::Connect(*(ObjPin **)(this + 4),*(ObjStatusViewer **)(this + 0xc));
        this[0x16] = (ConnectPinWrapper)param_1;
      }
    }
    CVar1 = (ConnectPinWrapper)0x0;
  }
  this[0x14] = CVar1;
  (*(code *)PTR_Unlock_0004c134)(*(undefined4 *)(this + 8));
  return;
}


/* 0002f5fc */

/* EventHandlerWrapper::SetEvent() */

void EventHandlerWrapper::SetEvent(void)

{
  int in_r0;
  
  (*(code *)PTR_SetSignal_0004c098)(in_r0 + 8);
  return;
}


/* 0002f60c */

/* EventHandlerWrapper::~EventHandlerWrapper() */

EventHandlerWrapper * __thiscall
EventHandlerWrapper::~EventHandlerWrapper(EventHandlerWrapper *this)

{
  *(int *)this = *(int *)(DAT_0002f638 + 0x2f61a + DAT_0002f63c) + 8;
  MWF::ObjSignal::~ObjSignal((ObjSignal *)(this + 8));
  MWF::EventHandler::~EventHandler((EventHandler *)this);
  return this;
}


/* 0002f640 */

/* EventHandlerWrapper::~EventHandlerWrapper() */

EventHandlerWrapper * __thiscall
EventHandlerWrapper::~EventHandlerWrapper(EventHandlerWrapper *this)

{
  ~EventHandlerWrapper(this);
  operator_delete(this);
  return this;
}


/* 0002f654 */

/* EventHandlerWrapper::EventHandlerWrapper() */

EventHandlerWrapper * __thiscall EventHandlerWrapper::EventHandlerWrapper(EventHandlerWrapper *this)

{
  int iVar1;
  
  iVar1 = DAT_0002f690;
  MWF::EventHandler::EventHandler((EventHandler *)this);
  *(int *)this = *(int *)(iVar1 + 0x2f666 + DAT_0002f694) + 8;
  MWF::ObjSignal::ObjSignal((ObjSignal *)(this + 8));
  MWF::ObjSignal::ClearSignal();
  return this;
}


/* 0002f698 */

/* EventHandlerWrapper::WaitEvent(unsigned int) */

void EventHandlerWrapper::WaitEvent(uint param_1)

{
  (*(code *)PTR_GetSignal_0004c1cc)(param_1 + 8);
  return;
}


/* 0002f6a8 */

/* MediaConfigWrapper::ERR_CNV(int) */

undefined4 MediaConfigWrapper::ERR_CNV(int param_1)

{
  if ((uint)param_1 < 2) {
    return *(undefined4 *)(DAT_0002f6c0 + 0x2f6b6 + param_1 * 4);
  }
  return 1;
}


/* 0002f6c4 */

/* MediaConfigWrapper::GetRsrcInhOffset(unsigned int, unsigned int*) */

int MediaConfigWrapper::GetRsrcInhOffset(uint param_1,uint *param_2)

{
  int iVar1;
  undefined4 local_54;
  undefined2 local_50;
  undefined2 local_4e;
  int local_40;
  uint local_3c;
  byte local_38;
  EventWrapper aEStack_34 [24];
  MonCtrl aMStack_1c [12];
  
  MonCtrl::MonCtrl(aMStack_1c,(char *)(DAT_0002f794 + 0x2f6d4),true);
  if ((param_2 == (uint *)0x0) || (param_1 == 0xffffffff)) {
    iVar1 = 3;
  }
  else {
    *param_2 = 0xffffffff;
    MemUtil::MemSet8(&local_54,'\0',0x20);
    local_54 = 0x1008;
    local_50 = 3;
    local_4e = 8;
    local_3c = param_1;
    MWF::EventWrapper::EventWrapper(aEStack_34);
    MWF::EventWrapper::SetSendId((uint)aEStack_34);
    iVar1 = MWF::EventWrapper::SendAndRecv(aEStack_34,(int)&local_54,(void *)0x20,0);
    if (iVar1 == 0) {
      if (local_40 == 0) {
        *param_2 = (uint)local_38;
      }
      else {
        MonCtrl::ConPrintfMessage((char *)aMStack_1c,DAT_0002f798 + 0x2f742);
        iVar1 = ERR_CNV(local_40);
      }
    }
    else {
      MonCtrl::ConPrintfMessage((char *)aMStack_1c,DAT_0002f79c + 0x2f75a,iVar1);
    }
    MWF::EventWrapper::~EventWrapper(aEStack_34);
  }
  MonCtrl::~MonCtrl(aMStack_1c);
  return iVar1;
}


/* 0002f7a0 */

/* MediaConfigWrapper::GetRsrcAcsrId(MediaConfigWrapper::RsrcType, unsigned int, DefRsrc::AcsrId_t*)
    */

int MediaConfigWrapper::GetRsrcAcsrId(int param_1,int param_2,undefined4 *param_3)

{
  int iVar1;
  undefined4 local_8c;
  undefined2 local_88;
  undefined2 local_86;
  int local_78;
  int local_74;
  undefined4 local_6c;
  undefined4 local_64;
  EventWrapper aEStack_30 [28];
  
  if (((param_3 == (undefined4 *)0x0) || (param_2 == 0)) || (param_2 == -1)) {
    iVar1 = 3;
  }
  else {
    MemUtil::MemSet8(&local_8c,'\0',0x5c);
    local_8c = 0x1006;
    local_88 = 3;
    local_86 = 0x44;
    local_74 = param_2;
    MWF::EventWrapper::EventWrapper(aEStack_30);
    MWF::EventWrapper::SetSendId((uint)aEStack_30);
    iVar1 = MWF::EventWrapper::SendAndRecv(aEStack_30,(int)&local_8c,(void *)0x5c,0);
    if (iVar1 == 0) {
      if (local_78 == 0) {
        if ((param_1 == 0) || (local_6c = local_64, param_1 == 1)) {
          *param_3 = local_6c;
        }
        else {
          iVar1 = 3;
        }
      }
      else {
        iVar1 = ERR_CNV(local_78);
      }
    }
    MWF::EventWrapper::~EventWrapper(aEStack_30);
  }
  return iVar1;
}


/* 0002f840 */

/* MediaConfigWrapper::DEVICE_TYPE_CNV(unsigned int) */

undefined4 MediaConfigWrapper::DEVICE_TYPE_CNV(uint param_1)

{
  if (param_1 < 10) {
    return *(undefined4 *)(DAT_0002f858 + 0x2f84e + param_1 * 4);
  }
  return 0;
}


/* 0002f85c */

/* MediaConfigWrapper::GetMediaInfo(unsigned int, MediaConfigWrapper::MediaConfigInfo*) */

int MediaConfigWrapper::GetMediaInfo(uint param_1,MediaConfigInfo *param_2)

{
  undefined2 uVar1;
  int iVar2;
  undefined4 uVar3;
  MediaConfigInfo *pMVar4;
  undefined4 *puVar5;
  uint uVar6;
  undefined4 local_128;
  undefined2 local_124;
  undefined2 local_122;
  int local_114;
  uint local_110;
  MediaConfigInfo local_10c;
  undefined2 local_10a;
  undefined1 auStack_108 [24];
  uint local_f0;
  MediaConfigInfo local_ec;
  uint local_e8;
  undefined2 local_e4 [14];
  undefined1 auStack_c8 [128];
  MediaConfigInfo local_48;
  EventWrapper aEStack_44 [24];
  MonCtrl aMStack_2c [16];
  
  puVar5 = &local_128;
  MonCtrl::MonCtrl(aMStack_2c,(char *)(DAT_0002f998 + 0x2f874),true);
  if ((param_1 == 0xffffffff) || (param_2 == (MediaConfigInfo *)0x0)) {
    iVar2 = 3;
  }
  else {
    MemUtil::MemSet8(param_2,'\0',200);
    MemUtil::MemSet8(puVar5,'\0',0xe4);
    local_128 = 0x1000;
    local_124 = 3;
    local_122 = 0xcc;
    local_110 = param_1;
    MWF::EventWrapper::EventWrapper(aEStack_44);
    MWF::EventWrapper::SetSendId((uint)aEStack_44);
    iVar2 = MWF::EventWrapper::SendAndRecv(aEStack_44,(int)puVar5,(void *)0xe4,0);
    if (iVar2 == 0) {
      if (local_114 == 0) {
        *param_2 = local_10c;
        *(undefined2 *)(param_2 + 2) = local_10a;
        MemUtil::MemCpy8(param_2 + 4,auStack_108,0x15);
        uVar3 = DEVICE_TYPE_CNV(local_f0);
        *(undefined4 *)(param_2 + 0x1c) = uVar3;
        param_2[0x20] = local_ec;
        pMVar4 = param_2;
        for (uVar6 = 0; uVar6 < (byte)param_2[0x20]; uVar6 = uVar6 + 1) {
          uVar3 = DEVICE_TYPE_CNV(puVar5[0x10]);
          uVar1 = *(undefined2 *)(puVar5 + 0x11);
          *(undefined4 *)(pMVar4 + 0x24) = uVar3;
          puVar5 = puVar5 + 2;
          *(undefined2 *)(pMVar4 + 0x28) = uVar1;
          pMVar4 = pMVar4 + 8;
        }
        MemUtil::MemCpy8(param_2 + 0x44,auStack_c8,0x80);
        param_2[0xc4] = local_48;
      }
      else {
        MonCtrl::ConPrintfMessage((char *)aMStack_2c,DAT_0002f99c + 0x2f944);
        iVar2 = ERR_CNV(local_114);
      }
    }
    else {
      MonCtrl::ConPrintfMessage((char *)aMStack_2c,DAT_0002f9a0 + 0x2f95c,iVar2);
    }
    MWF::EventWrapper::~EventWrapper(aEStack_44);
  }
  MonCtrl::~MonCtrl(aMStack_2c);
  return iVar2;
}


/* 0002f9a4 */

/* MediaConfigWrapper::GetDeviceType(unsigned int) */

undefined4 MediaConfigWrapper::GetDeviceType(uint param_1)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 local_118;
  undefined2 local_114;
  undefined2 local_112;
  int local_104;
  uint local_100;
  uint local_e0;
  EventWrapper aEStack_34 [24];
  MonCtrl aMStack_1c [16];
  
  MonCtrl::MonCtrl(aMStack_1c,(char *)(DAT_0002fa68 + 0x2f9b8),true);
  if (param_1 == 0xffffffff) {
    uVar2 = 0;
    goto LAB_0002fa3c;
  }
  MemUtil::MemSet8(&local_118,'\0',0xe4);
  local_118 = 0x1000;
  local_114 = 3;
  local_112 = 0xcc;
  local_100 = param_1;
  MWF::EventWrapper::EventWrapper(aEStack_34);
  MWF::EventWrapper::SetSendId((uint)aEStack_34);
  iVar1 = MWF::EventWrapper::SendAndRecv(aEStack_34,(int)&local_118,(void *)0xe4,0);
  if (iVar1 == 0) {
    if (local_104 != 0) {
      MonCtrl::ConPrintfMessage((char *)aMStack_1c,DAT_0002fa6c + 0x2fa18);
      ERR_CNV(local_104);
      goto LAB_0002fa2e;
    }
    uVar2 = DEVICE_TYPE_CNV(local_e0);
  }
  else {
    MonCtrl::ConPrintfMessage((char *)aMStack_1c,DAT_0002fa70 + 0x2fa2c,iVar1);
LAB_0002fa2e:
    uVar2 = 0;
  }
  MWF::EventWrapper::~EventWrapper(aEStack_34);
LAB_0002fa3c:
  MonCtrl::~MonCtrl(aMStack_1c);
  return uVar2;
}


/* 0002fa74 */

int FUN_0002fa74(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
                undefined4 param_5,undefined4 *param_6,undefined4 param_7)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 *local_24;
  
  iVar1 = DAT_0002fae0;
  if ((param_1 != 0) && (iVar1 = osal_valloc_msg_wait(param_1,&local_24,0x10,1), iVar1 == 0)) {
    *local_24 = param_2;
    local_24[1] = param_3;
    local_24[2] = param_4;
    local_24[-1] = param_7;
    local_24[3] = param_5;
    iVar1 = osal_snd_sync_msg(param_1);
    if ((iVar1 == 0) && (param_6 != (undefined4 *)0x0)) {
      *param_6 = *local_24;
      param_6[1] = local_24[1];
      uVar2 = local_24[3];
      param_6[2] = local_24[2];
      param_6[3] = uVar2;
    }
    osal_free_msg(param_1,local_24);
  }
  return iVar1;
}


/* 0002fae4 */

int FUN_0002fae4(undefined4 *param_1)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 *local_14;
  
  iVar2 = DAT_0002fb34;
  if ((param_1 != (undefined4 *)0x0) &&
     (iVar2 = osal_valloc_msg_wait(DAT_0002fb2c,&local_14,8,1), uVar1 = DAT_0002fb30, iVar2 == 0)) {
    uVar3 = param_1[1];
    *local_14 = *param_1;
    local_14[1] = uVar3;
    *local_14 = uVar1;
    iVar2 = osal_snd_sync_msg(DAT_0002fb2c,local_14);
    osal_free_msg(DAT_0002fb2c,local_14);
  }
  return iVar2;
}


/* 0002fb38 */

void FUN_0002fb38(undefined4 param_1,undefined4 param_2)

{
  (*(code *)PTR_memset_0004bde4)(param_1,0,param_2);
  return;
}


/* 0002fb48 */

/* UpmWrapper::UpmWrapper() */

void __thiscall UpmWrapper::UpmWrapper(UpmWrapper *this)

{
  *(int *)this = *(int *)(DAT_0002fb74 + 0x2fb50 + DAT_0002fb78) + 8;
  *(undefined4 *)(this + 8) = 0;
  *(undefined4 *)(this + 4) = 0;
  *(undefined4 *)(this + 0xc) = 0;
  *(undefined4 *)(this + 0x14) = 0;
  *(undefined4 *)(this + 0x10) = 0;
  *(undefined4 *)(this + 0x18) = 0;
  *(undefined4 *)(this + 0x20) = 0;
  *(undefined4 *)(this + 0x1c) = 0;
  *(undefined4 *)(this + 0x24) = 0;
  *(undefined4 *)(this + 0x2c) = 0;
  *(undefined4 *)(this + 0x28) = 0;
  *(undefined4 *)(this + 0x30) = 0;
  return;
}


/* 0002fb7c */

/* UpmWrapper::POWER_TYPE_CNV(int, UpmWrapper::PowerType*) */

undefined4 UpmWrapper::POWER_TYPE_CNV(int param_1,PowerType *param_2)

{
  undefined4 uVar1;
  
  if (param_2 == (PowerType *)0x0) {
    return 3;
  }
  if (param_1 != 1) {
    if (param_1 == 2) {
      uVar1 = 1;
    }
    else {
      uVar1 = 2;
      if (param_1 == -1) {
        *(undefined4 *)param_2 = 2;
        return 0;
      }
    }
    *(undefined4 *)param_2 = uVar1;
    return 0;
  }
  *(undefined4 *)param_2 = 0;
  return 0;
}


/* 0002fbac */

/* UpmWrapper::CallBackPointForPowerStatus(void*, void*) */

void UpmWrapper::CallBackPointForPowerStatus(void *param_1,void *param_2)

{
  PowerType aPStack_1c [8];
  
  if (param_2 != (void *)0x0) {
    if (param_1 != (void *)0x0) {
      POWER_TYPE_CNV(*(int *)((int)param_1 + 4),aPStack_1c);
      (**(code **)((int)param_2 + 0x10))(aPStack_1c,4,*(undefined4 *)((int)param_2 + 0x1c),0);
    }
    osal_free_msg(DAT_0002fbe0,param_1);
  }
  return;
}


/* 0002fbe4 */

/* UpmWrapper::CONNECT_STAT_CNV(int, UpmWrapper::ConnectStat*) */

undefined4 UpmWrapper::CONNECT_STAT_CNV(int param_1,ConnectStat *param_2)

{
  undefined4 uVar1;
  
  if (param_2 != (ConnectStat *)0x0) {
    switch(param_1) {
    case 1:
      *(undefined4 *)param_2 = 0;
      return 0;
    case 2:
      uVar1 = 1;
      break;
    case 3:
      uVar1 = 2;
      break;
    default:
      uVar1 = 3;
    }
    *(undefined4 *)param_2 = uVar1;
    return 0;
  }
  return 3;
}


/* 0002fc14 */

/* UpmWrapper::CallBackPointForBatteryLevel(void*, void*) */

void UpmWrapper::CallBackPointForBatteryLevel(void *param_1,void *param_2)

{
  int local_38;
  uint local_34 [3];
  undefined2 local_28;
  undefined1 local_26;
  MonCtrl aMStack_24 [16];
  
  if (param_2 != (void *)0x0) {
    MonCtrl::MonCtrl(aMStack_24,(char *)(DAT_0002fcd8 + 0x2fc2e),false);
    if (param_1 != (void *)0x0) {
      FUN_0002fb38(&local_38,0x14);
      local_38 = (int)*(char *)((int)param_1 + 0x1c);
      CONNECT_STAT_CNV((int)*(char *)((int)param_1 + 0x1e),(ConnectStat *)local_34);
      local_26 = 0;
      if ((local_34[0] < 2) && (*(short *)((int)param_1 + 0x12) == 2)) {
        local_28 = *(undefined2 *)((int)param_1 + 0x10);
        local_26 = 1;
        MonCtrl::ConPrintfMessage((char *)aMStack_24,DAT_0002fcdc + 0x2fc6e);
      }
      if ((*(char *)((int)param_1 + 0x1f) == '\x02') && (*(short *)((int)param_1 + 0xe) == 2)) {
        local_34[1] = 0;
        if (local_34[0] < 2) {
          local_34[2] = (uint)*(ushort *)((int)param_1 + 0xc);
          MonCtrl::ConPrintfMessage((char *)aMStack_24,DAT_0002fce0 + 0x2fc98);
        }
      }
      else {
        local_34[1] = 1;
      }
      (**(code **)((int)param_2 + 0x14))(&local_38,0x14,*(undefined4 *)((int)param_2 + 0x20),1);
    }
    osal_free_msg(DAT_0002fcd4,param_1);
    MonCtrl::~MonCtrl(aMStack_24);
  }
  return;
}


/* 0002fce4 */

/* UpmWrapper::BATTERY_CHECK_CNV(int, UpmWrapper::BatteryCheck*) */

undefined4 UpmWrapper::BATTERY_CHECK_CNV(int param_1,BatteryCheck *param_2)

{
  if (param_2 == (BatteryCheck *)0x0) {
    return 3;
  }
  if (param_1 != 2) {
    if (param_1 == 3) {
      *(undefined4 *)param_2 = 2;
    }
    else {
      *(undefined4 *)param_2 = 0;
    }
    return 0;
  }
  *(undefined4 *)param_2 = 1;
  return 0;
}


/* 0002fd10 */

/* UpmWrapper::OFF_TYPE_CNV(int, UpmWrapper::OffType*) */

undefined4 UpmWrapper::OFF_TYPE_CNV(int param_1,OffType *param_2)

{
  if (param_2 == (OffType *)0x0) {
    return 3;
  }
  if (param_1 != 0x1b) {
    if (param_1 == 0x1c) {
      *(undefined4 *)param_2 = 2;
    }
    else {
      *(undefined4 *)param_2 = 0;
    }
    return 0;
  }
  *(undefined4 *)param_2 = 1;
  return 0;
}


/* 0002fd3c */

/* UpmWrapper::TEMPERATURE_CNV(int, UpmWrapper::TemperatureRange*) */

undefined4 UpmWrapper::TEMPERATURE_CNV(int param_1,TemperatureRange *param_2)

{
  undefined4 uVar1;
  
  if (param_2 != (TemperatureRange *)0x0) {
    switch(param_1) {
    case 1:
      uVar1 = 0xffffffff;
      break;
    case 2:
      *(undefined4 *)param_2 = 0;
      return 0;
    case 3:
      uVar1 = 1;
      break;
    case 4:
      uVar1 = 2;
      break;
    case 5:
      uVar1 = 4;
      break;
    default:
      return 0;
    }
    *(undefined4 *)param_2 = uVar1;
    return 0;
  }
  return 3;
}


/* 0002fd78 */

/* UpmWrapper::CallBackPointForHeatAlart(void*, void*) */

void UpmWrapper::CallBackPointForHeatAlart(void *param_1,void *param_2)

{
  undefined4 local_20;
  uint local_1c;
  
  if (param_2 != (void *)0x0) {
    if (param_1 != (void *)0x0) {
      local_20 = 0;
      local_1c = (uint)(*(int *)((int)param_1 + 4) != 0);
      TEMPERATURE_CNV(*(int *)((int)param_1 + 8),(TemperatureRange *)&local_20);
      (**(code **)((int)param_2 + 0x18))(&local_20,8,*(undefined4 *)((int)param_2 + 0x24),2);
    }
    osal_free_msg(DAT_0002fdb8,param_1);
  }
  return;
}


/* 0002fdbc */

/* UpmWrapper::ERR_CNV(OSAL_ERR) */

undefined4 UpmWrapper::ERR_CNV(int param_1)

{
  if (param_1 == DAT_0002fdf4) {
    return 5;
  }
  if (param_1 < DAT_0002fdf4) {
    if (param_1 == -0x400) {
      return 3;
    }
  }
  else {
    if (param_1 == -0x3fc) {
      return 0x5001;
    }
    if (param_1 < -0x3fc) {
      return 0x5002;
    }
    if (param_1 == 0) {
      return 0;
    }
  }
  return 1;
}


/* 0002fdf8 */

/* UpmWrapper::GetTemperatureRange(UpmWrapper::TemperatureRangeTarget,
   UpmWrapper::TemperatureRange*) */

undefined4 UpmWrapper::GetTemperatureRange(int param_1,TemperatureRange *param_2)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 local_2c;
  int local_28;
  int local_24;
  undefined4 uStack_20;
  undefined4 *local_1c;
  
  if (param_2 != (TemperatureRange *)0x0) {
    *(undefined4 *)param_2 = 0;
    FUN_0002fb38(&local_2c,0x10);
    if ((param_1 == 0) || (param_1 == 1)) {
      local_28 = param_1;
      iVar2 = osal_valloc_msg_wait(DAT_0002fe84,&local_1c,0x10,1);
      puVar1 = local_1c;
      if (iVar2 == 0) {
        *local_1c = local_2c;
        local_1c[1] = local_28;
        local_1c[2] = local_24;
        local_1c[3] = uStack_20;
        uVar3 = DAT_0002fe84;
        *local_1c = DAT_0002fe88;
        iVar2 = osal_snd_sync_msg(uVar3,local_1c);
        if (iVar2 == 0) {
          local_2c = *puVar1;
          local_28 = puVar1[1];
          local_24 = puVar1[2];
          uStack_20 = puVar1[3];
          osal_free_msg(DAT_0002fe84,local_1c);
          uVar3 = TEMPERATURE_CNV(local_24,param_2);
          return uVar3;
        }
        osal_free_msg(DAT_0002fe84,local_1c);
      }
      uVar3 = ERR_CNV(iVar2);
      return uVar3;
    }
  }
  return 3;
}


/* 0002fe8c */

/* UpmWrapper::GetOffType(UpmWrapper::OffType*, unsigned int) */

undefined4 UpmWrapper::GetOffType(OffType *param_1,uint param_2)

{
  int iVar1;
  undefined4 uVar2;
  undefined1 auStack_24 [8];
  int local_1c;
  int local_14;
  
  if (param_1 == (OffType *)0x0) {
    uVar2 = 3;
  }
  else {
    *(undefined4 *)param_1 = 0;
    iVar1 = osal_dynamic_id(0x2a,param_2 & 0xffff,&local_14);
    if (iVar1 == 0) {
      iVar1 = DAT_0002fef8;
      if (local_14 != 0) {
        iVar1 = FUN_0002fa74(DAT_0002fef0,DAT_0002fef4,0,0,0,auStack_24,local_14);
      }
      osal_dynamic_id(0x4a,0,local_14);
      if (iVar1 == 0) {
        uVar2 = OFF_TYPE_CNV(local_1c,param_1);
        return uVar2;
      }
    }
    uVar2 = ERR_CNV(iVar1);
  }
  return uVar2;
}


/* 0002fefc */

/* UpmWrapper::SetBatterryCalcInfoForRSS(bool) */

void UpmWrapper::SetBatterryCalcInfoForRSS(bool param_1)

{
  undefined1 auStack_18 [4];
  undefined1 local_14;
  undefined1 local_13;
  
  FUN_0002fb38(auStack_18,8);
  local_14 = 0xc;
  if (param_1) {
    local_13 = 1;
  }
  else {
    local_13 = 2;
  }
  FUN_0002fae4(auStack_18);
  ERR_CNV();
  return;
}


/* 0002ff2c */

/* UpmWrapper::SetBatterryCalcInfoForMedia(bool, UpmWrapper::MediaCalcInfo) */

void UpmWrapper::SetBatterryCalcInfoForMedia(int param_1,undefined4 param_2)

{
  undefined1 auStack_18 [4];
  undefined1 local_14;
  undefined1 local_13;
  
  FUN_0002fb38(auStack_18,8);
  if (param_1 == 0) {
    local_14 = 4;
  }
  else {
    local_14 = 3;
  }
  switch(param_2) {
  default:
    local_13 = 0xff;
    break;
  case 1:
    local_13 = 1;
    break;
  case 2:
    local_13 = 2;
    break;
  case 3:
    local_13 = 3;
  }
  FUN_0002fae4(auStack_18);
  ERR_CNV();
  return;
}


/* 0002ff76 */

/* UpmWrapper::SetBatterryCalcInfoForMRec(UpmWrapper::MRecCalcInfo) */

void UpmWrapper::SetBatterryCalcInfoForMRec(undefined4 param_1)

{
  undefined1 auStack_18 [4];
  undefined1 local_14;
  undefined1 local_13;
  
  FUN_0002fb38(auStack_18,8);
  local_13 = 6;
  local_14 = 6;
  switch(param_1) {
  default:
    local_13 = 0xff;
    break;
  case 1:
    local_13 = 1;
    break;
  case 2:
    local_13 = 2;
    break;
  case 3:
    local_13 = 3;
    break;
  case 4:
    local_13 = 4;
    break;
  case 5:
    local_13 = 5;
    break;
  case 6:
    break;
  case 7:
    local_13 = 7;
    break;
  case 8:
    local_13 = 8;
    break;
  case 9:
    local_13 = 9;
    break;
  case 10:
    local_13 = 10;
    break;
  case 0xb:
    local_13 = 0xb;
    break;
  case 0xc:
    local_13 = 0xc;
    break;
  case 0xd:
    local_13 = 0xd;
    break;
  case 0xe:
    local_13 = 0xe;
    break;
  case 0xf:
    local_13 = 0xf;
    break;
  case 0x10:
    local_13 = 0x10;
    break;
  case 0x11:
    local_13 = 0x11;
    break;
  case 0x12:
    local_13 = 0x12;
    break;
  case 0x13:
    local_13 = 0x13;
    break;
  case 0x14:
    local_13 = 0x14;
    break;
  case 0x15:
    local_13 = 0x15;
    break;
  case 0x16:
    local_13 = 0x16;
    break;
  case 0x17:
    local_13 = 0x17;
    break;
  case 0x18:
    local_13 = 0x18;
    break;
  case 0x19:
    local_13 = 0x19;
    break;
  case 0x1a:
    local_13 = 0x1a;
    break;
  case 0x1b:
    local_13 = 0x1b;
    break;
  case 0x1c:
    local_13 = 0x1c;
  }
  FUN_0002fae4(auStack_18);
  ERR_CNV();
  return;
}


/* 00030034 */

/* UpmWrapper::ClearDisableAutoPowerOff(unsigned int) */

void UpmWrapper::ClearDisableAutoPowerOff(uint param_1)

{
  FUN_0002fa74(DAT_0003005c,DAT_00030058,param_1,0,0,0,param_1);
  (*(code *)PTR_ERR_CNV_0004c0d8)();
  return;
}


/* 00030060 */

/* UpmWrapper::SetDisableAutoPowerOff(unsigned int) */

void UpmWrapper::SetDisableAutoPowerOff(uint param_1)

{
  FUN_0002fa74(DAT_00030088,DAT_00030084,param_1,0,0,0,param_1);
  (*(code *)PTR_ERR_CNV_0004c0d8)();
  return;
}


/* 0003008c */

/* UpmWrapper::ReleaseId(unsigned int) */

void UpmWrapper::ReleaseId(uint param_1)

{
  osal_dynamic_id(0x4a,0,param_1);
  (*(code *)PTR_ERR_CNV_0004c0d8)();
  return;
}


/* 000300a2 */

/* UpmWrapper::GenerateId(unsigned int, unsigned int*) */

undefined4 UpmWrapper::GenerateId(uint param_1,uint *param_2)

{
  undefined4 uVar1;
  
  if (param_2 == (uint *)0x0) {
    return 3;
  }
  *param_2 = 0;
  osal_dynamic_id(0x2a,param_1 & 0xffff);
  uVar1 = (*(code *)PTR_ERR_CNV_0004c0d8)();
  return uVar1;
}


/* 000300c4 */

/* UpmWrapper::GetAcBatteryCheckInfo(UpmWrapper::PowerType*, unsigned int*,
   UpmWrapper::BatteryCheckInfo*, UpmWrapper::ThresholdValue) */

int UpmWrapper::GetAcBatteryCheckInfo(PowerType *param_1,int *param_2,int *param_3,int param_4)

{
  undefined4 uVar1;
  undefined4 *puVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  undefined4 *puVar8;
  undefined4 local_6c;
  undefined4 uStack_68;
  undefined4 uStack_64;
  undefined4 local_60;
  undefined4 local_5c;
  undefined4 uStack_58;
  undefined4 uStack_54;
  undefined4 local_50;
  undefined1 auStack_4c [4];
  int local_48;
  int local_40;
  undefined1 auStack_3c [4];
  int local_38;
  undefined4 local_34;
  int local_30;
  undefined4 *local_2c [2];
  
  if (((param_1 == (PowerType *)0x0) || (param_2 == (int *)0x0)) || (param_3 == (int *)0x0)) {
    iVar3 = 3;
  }
  else {
    *(undefined4 *)param_1 = 2;
    *param_2 = 0;
    FUN_0002fb38(param_3,0x54);
    iVar3 = osal_valloc_msg_wait(DAT_000302a4,local_2c,0x14,1);
    uVar1 = DAT_000302a4;
    if (iVar3 == 0) {
      *local_2c[0] = DAT_000302a8;
      iVar3 = osal_snd_sync_msg(uVar1);
      if (iVar3 == 0) {
        iVar3 = local_2c[0][1];
        osal_free_msg(DAT_000302a4);
        iVar3 = POWER_TYPE_CNV(iVar3,param_1);
        if (iVar3 != 0) {
          return iVar3;
        }
        if (*(int *)param_1 != 1) {
          return 0;
        }
        FUN_0002fb38(auStack_3c,0x10);
        FUN_0002fb38(&local_6c,0x20);
        iVar3 = 1;
        do {
          iVar6 = iVar3;
          *param_3 = iVar6;
          local_50 = CONCAT31((int3)(local_50 >> 8),(char)iVar6) & 0xffff00ff;
          local_38 = iVar6;
          iVar3 = osal_valloc_msg_wait(DAT_000302ac,local_2c,0x20,1);
          puVar2 = local_2c[0];
          iVar7 = iVar6 + -1;
          if (iVar3 != 0) {
LAB_0003029c:
            iVar5 = ERR_CNV(iVar3);
            break;
          }
          *local_2c[0] = local_6c;
          local_2c[0][1] = uStack_68;
          local_2c[0][2] = uStack_64;
          local_2c[0][3] = local_60;
          puVar8 = local_2c[0] + 4;
          *puVar8 = local_5c;
          local_2c[0][5] = uStack_58;
          local_2c[0][6] = uStack_54;
          local_2c[0][7] = local_50;
          uVar1 = DAT_000302ac;
          *local_2c[0] = DAT_000302a8;
          iVar3 = osal_snd_sync_msg(uVar1,local_2c[0]);
          if (iVar3 != 0) {
            osal_free_msg(DAT_000302ac,local_2c[0]);
            goto LAB_0003029c;
          }
          local_6c = *puVar2;
          uStack_68 = puVar2[1];
          uStack_64 = puVar2[2];
          local_60 = puVar2[3];
          local_5c = *puVar8;
          uStack_58 = puVar2[5];
          uStack_54 = puVar2[6];
          local_50 = puVar2[7];
          osal_free_msg(DAT_000302ac,local_2c[0]);
          iVar4 = CONNECT_STAT_CNV((int)local_50._2_1_,(ConnectStat *)(param_3 + 1));
          iVar5 = iVar4;
          if (iVar4 != 0) break;
          *(undefined1 *)(param_3 + 6) = 0;
          if (((uint)param_3[1] < 2) && (local_5c._2_2_ == 2)) {
            *(undefined2 *)(param_3 + 4) = (undefined2)local_5c;
            *(undefined1 *)(param_3 + 6) = 1;
          }
          param_3[2] = 2;
          if ((uint)param_3[1] < 2) {
            if ((local_50._3_1_ == '\x02') && (local_60._2_2_ == 2)) {
              param_3[3] = local_60 & 0xffff;
              iVar3 = 0;
            }
            else {
              if (local_60._2_2_ != 3) goto LAB_00030224;
              iVar3 = 1;
            }
            param_3[2] = iVar3;
          }
LAB_00030224:
          if (param_4 == 1) {
            local_34 = DAT_000302b0;
LAB_00030234:
            memset(auStack_4c,0,0x10);
            iVar3 = FUN_0002fa74(DAT_000302b4,DAT_000302a8,local_38,local_34,local_30,auStack_4c,
                                 DAT_000302b8);
            if ((iVar3 != 0) || (iVar3 = local_48, local_48 != 0)) goto LAB_0003029c;
            local_30 = local_40;
            iVar5 = BATTERY_CHECK_CNV(local_40,(BatteryCheck *)(param_3 + 5));
            if (iVar5 != 0) break;
          }
          else if (param_4 != 0) goto LAB_00030234;
          param_3 = param_3 + 7;
          iVar5 = iVar4;
          iVar3 = iVar6 + 1;
          iVar7 = iVar6;
        } while (iVar6 + 1 != 4);
        *param_2 = iVar7;
        return iVar5;
      }
      osal_free_msg(DAT_000302a4,local_2c[0]);
    }
    iVar3 = ERR_CNV(iVar3);
  }
  return iVar3;
}


/* 000302bc */

/* UpmWrapper::ClearCallBackForHeatAlert() */

void __thiscall UpmWrapper::ClearCallBackForHeatAlert(UpmWrapper *this)

{
  int iVar1;
  
  if ((*(int *)(this + 0x18) == 0) ||
     (iVar1 = osal_unreg_msg_queue_cb(DAT_000302f0,*(undefined4 *)(this + 0x30)), iVar1 == 0)) {
    if (*(int *)(this + 0xc) != 0) {
      osal_dynamic_id(0x4a,0);
      *(undefined4 *)(this + 0xc) = 0;
    }
    *(undefined4 *)(this + 0x18) = 0;
    *(undefined4 *)(this + 0x24) = 0;
    *(undefined4 *)(this + 0x30) = 0;
  }
  (*(code *)PTR_ERR_CNV_0004c0d8)();
  return;
}


/* 000302f4 */

/* UpmWrapper::RegisterCallBackForHeatAlert(unsigned int, void (*)(void*, int, void*, unsigned int),
   void*) */

int __thiscall
UpmWrapper::RegisterCallBackForHeatAlert
          (UpmWrapper *this,uint param_1,_func_void_void_ptr_int_void_ptr_uint *param_2,
          void *param_3)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined4 local_24;
  
  iVar1 = ClearCallBackForHeatAlert(this);
  iVar3 = DAT_00030364 + 0x3030e;
  if (iVar1 == 0) {
    iVar2 = osal_dynamic_id(0x2a,param_1 & 0xffff,&local_24);
    if (iVar2 == 0) {
      osal_reg_msg_queue_cb(DAT_00030360,this + 0x30,*(undefined4 *)(iVar3 + DAT_00030368),this);
    }
    iVar1 = ERR_CNV();
    if (iVar1 == 0) {
      *(_func_void_void_ptr_int_void_ptr_uint **)(this + 0x18) = param_2;
      *(void **)(this + 0x24) = param_3;
      *(undefined4 *)(this + 0xc) = local_24;
    }
    else if (iVar2 == 0) {
      osal_dynamic_id(0x4a,0,local_24);
    }
  }
  return iVar1;
}


/* 0003036c */

/* UpmWrapper::ClearCallBackForBatteryLevel() */

void __thiscall UpmWrapper::ClearCallBackForBatteryLevel(UpmWrapper *this)

{
  int iVar1;
  
  if ((*(int *)(this + 0x14) == 0) ||
     (iVar1 = osal_unreg_msg_queue_cb(DAT_000303a0,*(undefined4 *)(this + 0x2c)), iVar1 == 0)) {
    if (*(int *)(this + 8) != 0) {
      osal_dynamic_id(0x4a,0);
      *(undefined4 *)(this + 8) = 0;
    }
    *(undefined4 *)(this + 0x14) = 0;
    *(undefined4 *)(this + 0x20) = 0;
    *(undefined4 *)(this + 0x2c) = 0;
  }
  (*(code *)PTR_ERR_CNV_0004c0d8)();
  return;
}


/* 000303a4 */

/* UpmWrapper::RegisterCallBackForBatteryLevel(unsigned int, void (*)(void*, int, void*, unsigned
   int), void*) */

int __thiscall
UpmWrapper::RegisterCallBackForBatteryLevel
          (UpmWrapper *this,uint param_1,_func_void_void_ptr_int_void_ptr_uint *param_2,
          void *param_3)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined4 local_24;
  
  iVar1 = ClearCallBackForBatteryLevel(this);
  iVar3 = DAT_00030414 + 0x303be;
  if (iVar1 == 0) {
    iVar2 = osal_dynamic_id(0x2a,param_1 & 0xffff,&local_24);
    if (iVar2 == 0) {
      osal_reg_msg_queue_cb(DAT_00030410,this + 0x2c,*(undefined4 *)(iVar3 + DAT_00030418),this);
    }
    iVar1 = ERR_CNV();
    if (iVar1 == 0) {
      *(_func_void_void_ptr_int_void_ptr_uint **)(this + 0x14) = param_2;
      *(void **)(this + 0x20) = param_3;
      *(undefined4 *)(this + 8) = local_24;
    }
    else if (iVar2 == 0) {
      osal_dynamic_id(0x4a,0,local_24);
    }
  }
  return iVar1;
}


/* 0003041c */

/* UpmWrapper::ClearCallBackForPowerStatus() */

void __thiscall UpmWrapper::ClearCallBackForPowerStatus(UpmWrapper *this)

{
  int iVar1;
  
  if ((*(int *)(this + 0x10) == 0) ||
     (iVar1 = osal_unreg_msg_queue_cb(DAT_00030450,*(undefined4 *)(this + 0x28)), iVar1 == 0)) {
    if (*(int *)(this + 4) != 0) {
      osal_dynamic_id(0x4a,0);
      *(undefined4 *)(this + 4) = 0;
    }
    *(undefined4 *)(this + 0x10) = 0;
    *(undefined4 *)(this + 0x1c) = 0;
    *(undefined4 *)(this + 0x28) = 0;
  }
  (*(code *)PTR_ERR_CNV_0004c0d8)();
  return;
}


/* 00030454 */

/* UpmWrapper::~UpmWrapper() */

UpmWrapper * __thiscall UpmWrapper::~UpmWrapper(UpmWrapper *this)

{
  *(int *)this = *(int *)(DAT_00030494 + 0x30462 + DAT_00030498) + 8;
  ClearCallBackForBatteryLevel(this);
  ClearCallBackForPowerStatus(this);
  ClearCallBackForHeatAlert(this);
  *(undefined4 *)(this + 8) = 0;
  *(undefined4 *)(this + 4) = 0;
  *(undefined4 *)(this + 0xc) = 0;
  *(undefined4 *)(this + 0x14) = 0;
  *(undefined4 *)(this + 0x10) = 0;
  *(undefined4 *)(this + 0x18) = 0;
  *(undefined4 *)(this + 0x20) = 0;
  *(undefined4 *)(this + 0x1c) = 0;
  *(undefined4 *)(this + 0x24) = 0;
  *(undefined4 *)(this + 0x2c) = 0;
  *(undefined4 *)(this + 0x28) = 0;
  *(undefined4 *)(this + 0x30) = 0;
  return this;
}


/* 0003049c */

/* UpmWrapper::~UpmWrapper() */

UpmWrapper * __thiscall UpmWrapper::~UpmWrapper(UpmWrapper *this)

{
  ~UpmWrapper(this);
  operator_delete(this);
  return this;
}


/* 000304b0 */

/* UpmWrapper::RegisterCallBackForPowerStatus(unsigned int, void (*)(void*, int, void*, unsigned
   int), void*) */

int __thiscall
UpmWrapper::RegisterCallBackForPowerStatus
          (UpmWrapper *this,uint param_1,_func_void_void_ptr_int_void_ptr_uint *param_2,
          void *param_3)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined4 local_24;
  
  iVar1 = ClearCallBackForPowerStatus(this);
  iVar3 = DAT_00030520 + 0x304ca;
  if (iVar1 == 0) {
    iVar2 = osal_dynamic_id(0x2a,param_1 & 0xffff,&local_24);
    if (iVar2 == 0) {
      osal_reg_msg_queue_cb(DAT_0003051c,this + 0x28,*(undefined4 *)(iVar3 + DAT_00030524),this);
    }
    iVar1 = ERR_CNV();
    if (iVar1 == 0) {
      *(_func_void_void_ptr_int_void_ptr_uint **)(this + 0x10) = param_2;
      *(void **)(this + 0x1c) = param_3;
      *(undefined4 *)(this + 4) = local_24;
    }
    else if (iVar2 == 0) {
      osal_dynamic_id(0x4a,0,local_24);
    }
  }
  return iVar1;
}


/* 00030528 */

int FUN_00030528(void *param_1,void *param_2)

{
  int iVar1;
  undefined4 local_40 [4];
  undefined2 local_30;
  short local_2e;
  undefined1 auStack_2c [10];
  undefined1 auStack_22 [14];
  
  if ((param_1 != (void *)0x0) || (iVar1 = DAT_00030588, param_2 != (void *)0x0)) {
    memset(local_40,0,0x28);
    local_40[0] = 0x28;
    local_30 = 2;
    iVar1 = osal_snd_sync_direct(DAT_00030584,local_40);
    if (iVar1 == 0) {
      iVar1 = (int)local_2e;
    }
    if (param_1 != (void *)0x0) {
      memcpy(param_1,auStack_2c,10);
    }
    if (param_2 != (void *)0x0) {
      memcpy(param_2,auStack_22,6);
    }
  }
  return iVar1;
}


/* 0003058c */

void FUN_0003058c(undefined4 param_1,code *param_2)

{
  (*param_2)();
  (*(code *)PTR_osal_free_msg_0004c340)(DAT_000305a0,param_1);
  return;
}


/* 000305a4 */

void FUN_000305a4(void)

{
  (*(code *)PTR_pthread_mutex_unlock_0004bed0)(*(int *)(DAT_000305bc + 0x305ac + DAT_000305c0) + 4);
  return;
}


/* 000305c4 */

/* UtimeWrapper::CallbackPointForDateChgNotify(OSAL_DATECHG_NOTIFY const*) */

void UtimeWrapper::CallbackPointForDateChgNotify(OSAL_DATECHG_NOTIFY *param_1)

{
  code *pcVar1;
  int iVar2;
  
  iVar2 = DAT_000305f8 + 0x305d2;
  MWF::ObjLock::Lock(*(ObjLock **)(iVar2 + DAT_000305fc));
  if (**(int **)(iVar2 + DAT_00030600) != 0) {
    if (((*(undefined4 **)(iVar2 + DAT_00030604))[1] != 0) &&
       (pcVar1 = (code *)**(undefined4 **)(iVar2 + DAT_00030604), pcVar1 != (code *)0x0)) {
      (*pcVar1)(param_1);
    }
  }
  FUN_000305a4();
  return;
}


/* 00030608 */

/* UtimeWrapper::RegisterCallbackForDateChgNotify(void (*)(OSAL_DATECHG_NOTIFY const*, void*),
   void*) */

undefined4
UtimeWrapper::RegisterCallbackForDateChgNotify
          (_func_void_OSAL_DATECHG_NOTIFY_ptr_void_ptr *param_1,void *param_2)

{
  undefined4 *puVar1;
  undefined4 uVar2;
  int *piVar3;
  int iVar4;
  MonCtrl aMStack_2c [16];
  
  iVar4 = DAT_000306c0 + 0x3061a;
  if ((param_1 != (_func_void_OSAL_DATECHG_NOTIFY_ptr_void_ptr *)0x0) && (param_2 != (void *)0x0)) {
    MWF::ObjLock::Lock(*(ObjLock **)(iVar4 + DAT_000306c4));
    piVar3 = *(int **)(iVar4 + DAT_000306c8);
    if ((*piVar3 == 0) &&
       (puVar1 = *(undefined4 **)(iVar4 + DAT_000306cc), param_2 != (void *)puVar1[1])) {
      iVar4 = osal_reg_msg_queue_cb
                        (DAT_000306bc,*(undefined4 *)(iVar4 + DAT_000306d0),DAT_000306d4 + 0x30656,
                         *(undefined4 *)(iVar4 + DAT_000306d8));
      if (iVar4 == 0) {
        if (puVar1[1] == 0) {
          iVar4 = *piVar3;
          *puVar1 = param_1;
          puVar1[1] = param_2;
          *piVar3 = iVar4 + 1;
          uVar2 = 0;
        }
        else {
          uVar2 = 3;
        }
        FUN_000305a4();
        return uVar2;
      }
      MonCtrl::MonCtrl(aMStack_2c,(char *)(DAT_000306dc + 0x3066c),true);
      MonCtrl::ConPrintfMessage((char *)aMStack_2c,DAT_000306e0 + 0x30678,iVar4);
      FUN_000305a4();
      MonCtrl::~MonCtrl(aMStack_2c);
    }
    else {
      FUN_000305a4();
    }
  }
  return 3;
}


/* 000306e4 */

/* UtimeWrapper::ClearCallbackForDateChgNotify(void*) */

undefined4 UtimeWrapper::ClearCallbackForDateChgNotify(void *param_1)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  MonCtrl aMStack_1c [12];
  
  iVar4 = DAT_0003076c + 0x306f2;
  if (param_1 == (void *)0x0) {
    uVar3 = 3;
  }
  else {
    MWF::ObjLock::Lock(*(ObjLock **)(iVar4 + DAT_00030770));
    puVar1 = *(undefined4 **)(iVar4 + DAT_00030774);
    if (param_1 == (void *)puVar1[1]) {
      uVar3 = 0;
      *puVar1 = 0;
      puVar1[1] = 0;
      iVar2 = **(int **)(iVar4 + DAT_00030778) + -1;
      **(int **)(iVar4 + DAT_00030778) = iVar2;
      if ((iVar2 == 0) &&
         (iVar4 = osal_unreg_msg_queue_cb(DAT_00030768,**(undefined4 **)(iVar4 + DAT_0003077c)),
         uVar3 = 0, iVar4 != 0)) {
        MonCtrl::MonCtrl(aMStack_1c,(char *)(DAT_00030780 + 0x30732),true);
        MonCtrl::ConPrintfMessage((char *)aMStack_1c,DAT_00030784 + 0x3073e,iVar4);
        uVar3 = 0;
        MonCtrl::~MonCtrl(aMStack_1c);
      }
    }
    else {
      uVar3 = 3;
    }
    FUN_000305a4();
  }
  return uVar3;
}


/* 00030788 */

/* UtimeWrapper::USleep(unsigned long long) */

void __thiscall UtimeWrapper::USleep(UtimeWrapper *this,ulonglong param_1)

{
  int iVar1;
  undefined4 local_50 [5];
  int local_3c;
  UtimeWrapper *local_38;
  MonCtrl aMStack_24 [16];
  
  memset(local_50,0,0x28);
  local_50[0] = 0x28;
  local_38 = this;
  iVar1 = osal_snd_sync_direct(DAT_000307f0,local_50);
  if ((iVar1 != 0) || (iVar1 = local_3c, local_3c != 0)) {
    MonCtrl::MonCtrl(aMStack_24,(char *)(DAT_000307f4 + 0x307c0),true);
    MonCtrl::ConPrintfMessage((char *)aMStack_24,DAT_000307f8 + 0x307ce,iVar1);
    MonCtrl::~MonCtrl(aMStack_24);
  }
  return;
}


/* 00030800 */

/* UtimeWrapper::MSleep(unsigned long long) */

void __thiscall UtimeWrapper::MSleep(UtimeWrapper *this,ulonglong param_1)

{
  uint in_r1;
  bool bVar1;
  
  for (; DAT_00030854 <= in_r1 && (uint)(this <= DAT_00030850) <= DAT_00030854 - in_r1;
      in_r1 = in_r1 + DAT_0003084c + (uint)bVar1) {
    USleep(DAT_00030858,CONCAT44(DAT_00030854,DAT_00030850));
    bVar1 = CARRY4((uint)this,DAT_00030848);
    this = this + DAT_00030848;
  }
  (*(code *)PTR_USleep_0004be90)
            ((int)(ZEXT48(this) * 1000),in_r1 * 1000 + (int)(ZEXT48(this) * 1000 >> 0x20));
  return;
}


/* 00030860 */

/* UtimeWrapper::Sleep(unsigned long long) */

void __thiscall UtimeWrapper::Sleep(UtimeWrapper *this,ulonglong param_1)

{
  uint in_r1;
  bool bVar1;
  
  for (; DAT_000308b8 <= in_r1 && (uint)(this <= DAT_000308b4) <= DAT_000308b8 - in_r1;
      in_r1 = in_r1 + DAT_000308b0 + (uint)bVar1) {
    USleep(DAT_000308a4,CONCAT44(DAT_000308b8,DAT_000308b4));
    bVar1 = CARRY4((uint)this,DAT_000308ac);
    this = this + DAT_000308ac;
  }
  (*(code *)PTR_USleep_0004be90)
            ((int)(ZEXT48(this) * (ulonglong)DAT_000308a0),
             DAT_000308a0 * in_r1 + (int)(ZEXT48(this) * (ulonglong)DAT_000308a0 >> 0x20));
  return;
}


/* 000308c0 */

/* UtimeWrapper::GetSysCnt() */

undefined8 UtimeWrapper::GetSysCnt(void)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 local_48 [5];
  int local_34;
  undefined4 local_30;
  undefined4 uStack_2c;
  MonCtrl aMStack_24 [16];
  
  memset(local_48,0,0x20);
  local_48[0] = 0x20;
  iVar1 = osal_snd_sync_direct(DAT_00030928,local_48);
  if (iVar1 == 0) {
    iVar1 = local_34;
  }
  uVar2 = local_30;
  if (iVar1 != 0) {
    MonCtrl::MonCtrl(aMStack_24,(char *)(DAT_0003092c + 0x308f4),true);
    MonCtrl::ConPrintfMessage((char *)aMStack_24,DAT_00030930 + 0x30902,iVar1);
    uVar2 = 0;
    MonCtrl::~MonCtrl(aMStack_24);
    uStack_2c = 0;
  }
  return CONCAT44(uStack_2c,uVar2);
}


/* 00030934 */

/* UtimeWrapper::GetElapsedSysCnt(unsigned long long) */

longlong UtimeWrapper::GetElapsedSysCnt(ulonglong param_1)

{
  undefined4 in_r2;
  undefined4 in_r3;
  longlong lVar1;
  
  lVar1 = GetSysCnt();
  return lVar1 - CONCAT44(in_r3,in_r2);
}


/* 00030950 */

/* UtimeWrapper::TIME_CNV(OSAL_TIME*, UtimeWrapper::Time*) */

undefined4 UtimeWrapper::TIME_CNV(OSAL_TIME *param_1,Time *param_2)

{
  undefined2 uVar1;
  
  if (param_1 == (OSAL_TIME *)0x0) {
    return 3;
  }
  if (param_2 == (Time *)0x0) {
    return 3;
  }
  *(undefined2 *)param_2 = *(undefined2 *)param_1;
  *(OSAL_TIME *)(param_2 + 2) = param_1[2];
  *(OSAL_TIME *)(param_2 + 3) = param_1[3];
  *(OSAL_TIME *)(param_2 + 4) = param_1[4];
  *(OSAL_TIME *)(param_2 + 5) = param_1[5];
  *(OSAL_TIME *)(param_2 + 6) = param_1[6];
  switch(*(undefined2 *)(param_1 + 8)) {
  case 0:
    uVar1 = 0;
    break;
  case 1:
    uVar1 = 1;
    goto LAB_0003099e;
  case 2:
    *(undefined2 *)(param_2 + 8) = 2;
    return 0;
  case 3:
    uVar1 = 3;
    break;
  case 4:
    uVar1 = 4;
LAB_0003099e:
    *(undefined2 *)(param_2 + 8) = uVar1;
    return 0;
  default:
    *(undefined2 *)(param_2 + 8) = 4;
    return 0xffff;
  }
  *(undefined2 *)(param_2 + 8) = uVar1;
  return 0;
}


/* 000309b4 */

/* UtimeWrapper::TIMEZONE_CNV(OSAL_TIMEZONE*, UtimeWrapper::Timezone*) */

undefined4 UtimeWrapper::TIMEZONE_CNV(OSAL_TIMEZONE *param_1,Timezone *param_2)

{
  short sVar1;
  
  if (param_1 == (OSAL_TIMEZONE *)0x0) {
    return 3;
  }
  if (param_2 != (Timezone *)0x0) {
    *(undefined2 *)param_2 = *(undefined2 *)param_1;
    sVar1 = *(short *)(param_1 + 4);
    *(undefined2 *)(param_2 + 2) = *(undefined2 *)(param_1 + 2);
    if ((sVar1 != 1) && (sVar1 != 2)) {
      if (sVar1 == 0) {
        *(undefined2 *)(param_2 + 4) = 0;
        return 0;
      }
      *(undefined2 *)(param_2 + 4) = 2;
      return 0xffff;
    }
    *(short *)(param_2 + 4) = sVar1;
    return 0;
  }
  return 3;
}


/* 000309f0 */

/* UtimeWrapper::ERR_CNV(OSAL_ERR) */

undefined4 UtimeWrapper::ERR_CNV(int param_1)

{
  if (param_1 == DAT_00030a28) {
    return 5;
  }
  if (param_1 < DAT_00030a28) {
    if (param_1 == -0x400) {
      return 3;
    }
  }
  else {
    if (param_1 == -0x3fc) {
      return 0x5001;
    }
    if (param_1 < -0x3fc) {
      return 0x5002;
    }
    if (param_1 == 0) {
      return 0;
    }
  }
  return 1;
}


/* 00030a2c */

/* UtimeWrapper::GetDate(MPR::T_LTM*) */

void UtimeWrapper::GetDate(T_LTM *param_1)

{
  undefined2 local_24;
  T_LTM local_22;
  T_LTM local_21;
  T_LTM local_20;
  T_LTM local_1f;
  T_LTM local_1e;
  undefined2 local_18 [6];
  
  FUN_00030528(&local_24,local_18);
  *(undefined2 *)param_1 = local_18[0];
  *(undefined2 *)(param_1 + 2) = local_24;
  param_1[4] = local_22;
  param_1[5] = local_21;
  param_1[6] = local_20;
  param_1[7] = local_1f;
  param_1[8] = local_1e;
  ERR_CNV();
  return;
}


/* 00030a66 */

/* UtimeWrapper::GetDate(DefStruct::LocalTime*) */

void UtimeWrapper::GetDate(LocalTime *param_1)

{
  undefined2 local_24;
  LocalTime local_22;
  LocalTime local_21;
  LocalTime local_20;
  LocalTime local_1f;
  LocalTime local_1e;
  undefined2 local_18 [6];
  
  FUN_00030528(&local_24,local_18);
  *(undefined2 *)param_1 = local_18[0];
  *(undefined2 *)(param_1 + 2) = local_24;
  param_1[4] = local_22;
  param_1[5] = local_21;
  param_1[6] = local_20;
  param_1[7] = local_1f;
  param_1[8] = local_1e;
  ERR_CNV();
  return;
}


/* 00030aa0 */

/* UtimeWrapper::GetDate(UtimeWrapper::Time*, UtimeWrapper::Timezone*) */

void UtimeWrapper::GetDate(Time *param_1,Timezone *param_2)

{
  OSAL_TIME *pOVar1;
  undefined4 uVar2;
  OSAL_TIMEZONE *pOVar3;
  OSAL_TIME aOStack_2c [12];
  OSAL_TIMEZONE aOStack_20 [12];
  
  pOVar1 = (OSAL_TIME *)0x0;
  if (param_1 != (Time *)0x0) {
    pOVar1 = aOStack_2c;
  }
  if (param_2 == (Timezone *)0x0) {
    pOVar3 = (OSAL_TIMEZONE *)0x0;
  }
  else {
    pOVar3 = aOStack_20;
  }
  uVar2 = FUN_00030528(pOVar1,pOVar3);
  if (param_1 != (Time *)0x0) {
    TIME_CNV(aOStack_2c,param_1);
  }
  if (param_2 != (Timezone *)0x0) {
    TIMEZONE_CNV(aOStack_20,param_2);
  }
  ERR_CNV(uVar2);
  return;
}


/* 00030ae4 */

void _INIT_2(void)

{
  int iVar1;
  ObjLock *this;
  
  iVar1 = DAT_00030b08 + 0x30af0;
  this = *(ObjLock **)(iVar1 + DAT_00030b0c);
  MWF::ObjLock::ObjLock(this);
  (*(code *)PTR___aeabi_atexit_0004c184)
            (this,*(undefined4 *)(iVar1 + DAT_00030b10),*(undefined4 *)(iVar1 + DAT_00030b14));
  return;
}


/* 00030b18 */

void _fini(void)

{
  return;
}


/* 0004e000 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MprIf::NewFlashAviMMgr(FlashAviCreateParam *param_1,ulong *param_2)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e004 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void StrUtil::StrHexToUInt32(char *param_1)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e008 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int open(char *__file,int __oflag,...)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e00c */

/* WARNING: Control flow encountered bad instruction data */

void __thiscall MWF::EventWrapper::EventWrapper(EventWrapper *this)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e010 */

/* WARNING: Control flow encountered bad instruction data */

void __thiscall MWF::EventReceiver::EventReceiver(EventReceiver *this)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e014 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MprIf::Init(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e018 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void * mmap(void *__addr,size_t __len,int __prot,int __flags,int __fd,__off_t __offset)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e01c */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MonCtrl::ConPutMessage(char *param_1)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e020 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MonCtrl::ConPrintf(char *param_1,...)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e024 */

/* WARNING: Control flow encountered bad instruction data */

void __thiscall MWF::EventHandler::EventHandler(EventHandler *this)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e028 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::EventWrapper::SetSendId(uint param_1)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e02c */

/* WARNING: Control flow encountered bad instruction data */

void __thiscall MWF::EventSender::EventSender(EventSender *this)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e030 */

/* WARNING: Control flow encountered bad instruction data */

void __aeabi_unwind_cpp_pr0(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e034 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::EventWrapper::SendAndRecv(void *param_1,int param_2,void *param_3,int param_4)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e038 */

/* WARNING: Control flow encountered bad instruction data */

void __thiscall MWF::ObjSignal::ObjSignal(ObjSignal *this)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e03c */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MprIf::SetCreateParam_SerialNumber(ulong param_1)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e040 */

/* WARNING: Control flow encountered bad instruction data */

void __thiscall MWF::ObjLock::~ObjLock(ObjLock *this)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e044 */

/* WARNING: Control flow encountered bad instruction data */

void __thiscall MonCtrl::MonCtrl(MonCtrl *this,char *param_1,bool param_2)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e048 */

/* WARNING: Control flow encountered bad instruction data */

void __cxa_guard_acquire(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e04c */

/* WARNING: Control flow encountered bad instruction data */

void Backup_read(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e050 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::ObjMsg::AddParam(uint param_1,Param *param_2)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e054 */

/* WARNING: Control flow encountered bad instruction data */

void __gmon_start__(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e058 */

/* WARNING: Control flow encountered bad instruction data */

void _Jv_RegisterClasses(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e05c */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void operator_delete(void *param_1)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e060 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MprIf::SetCreateParam_RecCamInfoParam(bool param_1)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e064 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

char * strncpy(char *__dest,char *__src,size_t __n)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e068 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MprIf::SetCreateParam_SupportMedia(ulong param_1)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e06c */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::InhMgr::UpdateInhFactor(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e070 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MonCtrl::ConPutDec(uint param_1)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e074 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MprIf::DeleteMMgr(ulong param_1)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e078 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void * memset(void *__s,int __c,size_t __n)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e07c */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::ParamStd_Template<unsigned_char,(MWF::Param::Type)4>::GetValue(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e080 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::ParamStd_Template<short,(MWF::Param::Type)5>::GetValue(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e084 */

/* WARNING: Control flow encountered bad instruction data */

void __cxa_end_cleanup(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e088 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

char * strrchr(char *__s,int __c)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e08c */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::EventWrapper::ClearCallBack(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e090 */

/* WARNING: Control flow encountered bad instruction data */

void __thiscall MWF::ObjMsg::ObjMsg(void *this)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e094 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::ObjPin::Connect(ObjPin *param_1,ObjStatusViewer *param_2)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e098 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::ParamStd_Template<unsigned_int,(MWF::Param::Type)8>::GetValue(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e09c */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::EventReceiver::RecvEvent(ObjMsg *param_1)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e0a0 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MprIf::SetAviManagedContentTypes(ulong param_1,ulong param_2)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e0a4 */

/* WARNING: Control flow encountered bad instruction data */

void __thiscall MWF::RsrcAcsr::RsrcAcsr(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e0a8 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MonCtrl::ConPutStr(char *param_1)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e0ac */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::ParamStd_Template<int,(MWF::Param::Type)7>::GetValue(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e0b0 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void free(void *__ptr)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e0b4 */

/* WARNING: Control flow encountered bad instruction data */

void Log::Set(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e0b8 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MonCtrl::ConPutCRLF(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e0bc */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int pthread_mutex_unlock(pthread_mutex_t *__mutex)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e0c0 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void StrUtil::StrICmp(char *param_1,char *param_2)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e0c4 */

/* WARNING: Control flow encountered bad instruction data */

void osal_rcv_msg_tmo(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e0c8 */

/* WARNING: Control flow encountered bad instruction data */

void osal_reg_msg_queue_cb(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e0cc */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MonLib::MonFlgAdd(char *param_1,s_fltdesc *param_2)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e0d4 */

/* WARNING: Control flow encountered bad instruction data */

void __thiscall MWF::InhMgr::InhMgr(InhMgr *this)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e0d8 */

/* WARNING: Control flow encountered bad instruction data */

void __cxa_guard_release(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e0dc */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MprIf::SetCallbackFunc
               (ulong param_1,_func_void_ulong_ulong_void_ptr_ulong_void_ptr *param_2,ulong param_3,
               void *param_4)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e0e0 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int pthread_mutex_lock(pthread_mutex_t *__mutex)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e0e4 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MprIf::SetCreateParam_GpsParam(bool param_1)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e0e8 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

size_t strlen(char *__s)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e0ec */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::EventReceiver::GenerateEventId(uint param_1)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e0f0 */

/* WARNING: Control flow encountered bad instruction data */

void __thiscall MWF::ObjLock::ObjLock(ObjLock *this)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e0f4 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MonLib::ConPutStr(char *param_1,bool param_2)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e0f8 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::ParamStd_Template<unsigned_int,(MWF::Param::Type)8>::ParamStd_Template(uint param_1)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e0fc */

/* WARNING: Control flow encountered bad instruction data */

void osal_valloc_msg_wait(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e100 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void * memcpy(void *__dest,void *__src,size_t __n)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e104 */

/* WARNING: Control flow encountered bad instruction data */

void MWF::ObjMsg::GetParam(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e108 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MprIf::NewHddAviMMgr(HddAviCreateParam *param_1,ulong *param_2)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e10c */

/* WARNING: Control flow encountered bad instruction data */

void osal_unreg_msg_queue_cb(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e110 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::Struct::GetSize(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e114 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MonLib::MonFlgDel(char *param_1)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e118 */

/* WARNING: Control flow encountered bad instruction data */

void __cxa_call_unexpected(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e11c */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::ObjSignal::ClearSignal(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e120 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::EventWrapper::RegisterCallBack
               (uint param_1,_func_void_void_ptr_int_void_ptr_uint *param_2,void *param_3)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e124 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MonCtrl::ConPutStr(char *param_1,uint param_2)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e128 */

/* WARNING: Control flow encountered bad instruction data */

void Backup_write(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e12c */

/* WARNING: Control flow encountered bad instruction data */

void osal_snd_msg(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e130 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

char * strncat(char *__dest,char *__src,size_t __n)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e134 */

/* WARNING: Control flow encountered bad instruction data */

void __aeabi_uidiv(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e138 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MonCtrl::ConPutStrAndCRLF(char *param_1)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e13c */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::ParamStd_Template<signed_char,(MWF::Param::Type)3>::GetValue(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e140 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MprIf::GetPreFirstMountInfo(PreFirstMountInfo *param_1,ulong param_2)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e144 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::RsrcAcsr::Release(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e148 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void * operator_new(uint param_1)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e14c */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MprIf::SetCreateParam_StillSizeInfo(StillSizeInfo *param_1,ulong param_2)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e150 */

/* WARNING: Control flow encountered bad instruction data */

void MWF::InhMgr::ChangeInhFactorStatus(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e154 */

/* WARNING: Control flow encountered bad instruction data */

void MprIf::SetCreateParam_dualRecStillInfo(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e158 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

char * strstr(char *__haystack,char *__needle)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e15c */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int close(int __fd)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e160 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void * operator_new__(uint param_1)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e164 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MprIf::Destroy(MprIf *param_1)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e168 */

/* WARNING: Control flow encountered bad instruction data */

void __thiscall
MWF::ParamStd_Template<unsigned_int,(MWF::Param::Type)8>::~ParamStd_Template
          (ParamStd_Template<unsigned_int,(MWF::Param::Type)8> *this)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e16c */

/* WARNING: Control flow encountered bad instruction data */

void __aeabi_uidivmod(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e170 */

/* WARNING: Control flow encountered bad instruction data */

void MWF::RsrcAcsr::Acquire(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e174 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::ObjSignal::SetSignal(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e178 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void StrUtil::StrDecToUInt32(char *param_1)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e17c */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::EventIdFactory::ReleaseId(uint param_1)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e180 */

/* WARNING: Control flow encountered bad instruction data */

void __thiscall MWF::EventWrapper::~EventWrapper(EventWrapper *this)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e188 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void * malloc(size_t __size)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e18c */

/* WARNING: Control flow encountered bad instruction data */

void __thiscall MonCtrl::~MonCtrl(MonCtrl *this)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e190 */

/* WARNING: Control flow encountered bad instruction data */

void __thiscall MWF::ObjMsg::ObjMsg(void *this,uint param_1,uint param_2)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e194 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MonCtrl::ConPutDec(uint param_1,uint param_2)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e198 */

/* WARNING: Control flow encountered bad instruction data */

void __thiscall MWF::ObjSignal::~ObjSignal(ObjSignal *this)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e19c */

/* WARNING: Control flow encountered bad instruction data */

void __cxa_allocate_exception(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e1a0 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::Struct::GetValue(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e1a4 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MonCtrl::ConPrintfMessage(char *param_1,...)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e1a8 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::ObjMsg::GetCategoryId(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e1ac */

/* WARNING: Control flow encountered bad instruction data */

void __aeabi_uldivmod(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e1b0 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MprIf::SetCreateParam_SupportContentTypes(ulong param_1)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e1b4 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MprIf::SetCallbackFunc
               (_func_void_ulong_ulong_void_ptr_ulong_void_ptr *param_1,ulong param_2,void *param_3)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e1b8 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::EventReceiver::SetEventHandler(EventHandler *param_1)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e1bc */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::ObjPin::Disconnect(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e1c0 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void operator_delete__(void *param_1)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e1c4 */

/* WARNING: Control flow encountered bad instruction data */

void __aeabi_atexit(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e1c8 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MonLib::MonCmdDel(char *param_1)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e1cc */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MprIf::NewDvdDcfMMgr(DvdDcfCreateParam *param_1,ulong *param_2)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e1d0 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MprIf::NewBgmMMgr(BgmCreateParam *param_1,ulong *param_2)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e1d4 */

/* WARNING: Control flow encountered bad instruction data */

void __cxa_throw(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e1d8 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MonCtrl::GetFlagPtr(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e1dc */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::ParamStd_Template<unsigned_short,(MWF::Param::Type)6>::GetValue(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e1e0 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::ObjSignal::GetSignal(uint param_1)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e1e4 */

/* WARNING: Control flow encountered bad instruction data */

void __thiscall MWF::ObjMsg::~ObjMsg(void *this)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e1e8 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::EventIdFactory::GetId(uint param_1,uint *param_2)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e1ec */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MprIf::SetCreateParam_RecTcUbParam(bool param_1)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e1f0 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MonLib::MonCmdParseSubCmd(s_cmd *param_1,int param_2,char **param_3)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e1f4 */

/* WARNING: Control flow encountered bad instruction data */

void __cxa_end_catch(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e1f8 */

/* WARNING: Control flow encountered bad instruction data */

void Backup_get_datasize(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e1fc */

/* WARNING: Control flow encountered bad instruction data */

void osal_dynamic_id(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e200 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MprIf::NewUsbAviMMgr(UsbAviCreateParam *param_1,ulong *param_2)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e204 */

/* WARNING: Control flow encountered bad instruction data */

void __aeabi_idivmod(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e208 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int munmap(void *__addr,size_t __len)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e20c */

/* WARNING: Control flow encountered bad instruction data */

void __thiscall MWF::RsrcMgr::RsrcMgr(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e210 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MprIf::NewSsdAviMMgr(SsdAviCreateParam *param_1,ulong *param_2)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e214 */

/* WARNING: Control flow encountered bad instruction data */

void __thiscall MWF::InhMgr::~InhMgr(InhMgr *this)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e218 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::ParamStd_Template<bool,(MWF::Param::Type)1>::GetValue(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e21c */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::UInt64::GetValue(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e220 */

/* WARNING: Control flow encountered bad instruction data */

void __cxa_begin_catch(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e224 */

/* WARNING: Control flow encountered bad instruction data */

void __thiscall MWF::EventHandler::~EventHandler(EventHandler *this)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e22c */

/* WARNING: Control flow encountered bad instruction data */

void Backup_read_4Byte(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e230 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MprIf::NewMsAviMMgr(MsAviCreateParam *param_1,ulong *param_2)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e234 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MonLib::MonCmdAdd(char *param_1,_func_bool_int_char_ptr_ptr *param_2,char *param_3)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e238 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::EventSender::SetEventReceiver(EventReceiver *param_1)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e23c */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MonCtrl::ConPutMessageHeader(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e240 */

/* WARNING: Control flow encountered bad instruction data */

void __gxx_personality_v0(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e244 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::ObjMsg::GetMessageId(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e248 */

/* WARNING: Control flow encountered bad instruction data */

void MWF::EventHandler::SetEventMessage(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e24c */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MprIf::Create(CreateParam *param_1,MprIf **param_2,bool param_3)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e250 */

/* WARNING: Control flow encountered bad instruction data */

void __aeabi_unwind_cpp_pr1(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e254 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MWF::Int64::GetValue(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e258 */

/* WARNING: Control flow encountered bad instruction data */

void osal_snd_sync_direct(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e25c */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int strcmp(char *__s1,char *__s2)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e260 */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void MprIf::SetCreateParam_MultiMovieRec(bool param_1)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e264 */

/* WARNING: Control flow encountered bad instruction data */

void __cxa_finalize(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e268 */

/* WARNING: Control flow encountered bad instruction data */

void osal_snd_sync_msg(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* 0004e26c */

/* WARNING: Control flow encountered bad instruction data */

void osal_free_msg(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}

