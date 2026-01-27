#================================================================
# caio.py
# module file for CONTEC Analog I/O device
#                                                CONTEC.Co., Ltd.
#================================================================
import ctypes
import ctypes.wintypes

caio_dll = ctypes.windll.LoadLibrary('caio.dll')


#----------------------------------------
# Type definition
#----------------------------------------
#----------------------------------------
# External Control Signal
#----------------------------------------
AIO_AIF_CLOCK = 0               # Analog input external clock
AIO_AIF_START = 1               # Analog input external start trigger
AIO_AIF_STOP = 2                # Analog input external stop trigger
AIO_AOF_CLOCK = 3               # Analog output external clock
AIO_AOF_START = 4               # Analog output external start trigger
AIO_AOF_STOP = 5                # Analog output external stop trigger
#----------------------------------------
# Input/Output Range
#----------------------------------------
PM10 = 0                        # +/-10V
PM5 = 1                         # +/-5V
PM25 = 2                        # +/-2.5V
PM125 = 3                       # +/-1.25V
PM1 = 4                         # +/-1V
PM0625 = 5                      # +/-0.625V
PM05 = 6                        # +/-0.5V
PM03125 = 7                     # +/-0.3125V
PM025 = 8                       # +/-0.25V
PM0125 = 9                      # +/-0.125V
PM01 = 10                       # +/-0.1V
PM005 = 11                      # +/-0.05V
PM0025 = 12                     # +/-0.025V
PM00125 = 13                    # +/-0.0125V
PM001 = 14                      # +/-0.01V
P10 = 50                        # 0 ~ 10V
P5 = 51                         # 0 ~ 5V
P4095 = 52                      # 0 ~ 4.095V
P25 = 53                        # 0 ~ 2.5V
P125 = 54                       # 0 ~ 1.25V
P1 = 55                         # 0 ~ 1V
P05 = 56                        # 0 ~ 0.5V
P025 = 57                       # 0 ~ 0.25V
P01 = 58                        # 0 ~ 0.1V
P005 = 59                       # 0 ~ 0.05V
P0025 = 60                      # 0 ~ 0.025V
P00125 = 61                     # 0 ~ 0.0125V
P001 = 62                       # 0 ~ 0.01V
P20MA = 100                     # 0 ~ 20mA
P4TO20MA = 101                  # 4 ~ 20mA
PM20MA = 102                    # +/-20mA
P1TO5 = 150                     # 1 ~ 5V
#----------------------------------------
# Analog Input Event
#----------------------------------------
AIE_START = 0x00000002          # Event that AD converting start conditions are satisfied
AIE_RPTEND = 0x00000010         # Event of repeat end
AIE_END = 0x00000020            # Event of device operation end
AIE_DATA_NUM = 0x00000080       # Event that data of the specified sampling times are stored
AIE_DATA_TSF = 0x00000100       # Event that data of the specified number are transferred
AIE_OFERR = 0x00010000          # Event of Overflow
AIE_SCERR = 0x00020000          # Event of sampling clock error
AIE_ADERR = 0x00040000          # Event of AD converting error
#----------------------------------------
# Analog Output Event
#----------------------------------------
AOE_START = 0x00000002          # Event that DA converting start conditions are satisfied
AOE_RPTEND = 0x00000010         # Event of repeat end
AOE_END = 0x00000020            # Event of device operation end
AOE_DATA_NUM = 0x00000080       # Event that data of the specified sampling times are output
AOE_DATA_TSF = 0x00000100       # Event that data of the specified number are transferred
AOE_SCERR = 0x00020000          # Event of sampling clock error
AOE_DAERR = 0x00040000          # Event of DA converting error
#----------------------------------------
# Counter Event
#----------------------------------------
CNTE_DATA_NUM = 0x00000010      # Event of count comparison match
CNTE_ORERR = 0x00010000         # Event of count overrun
CNTE_ERR = 0x00020000           # Counter operating error
#----------------------------------------
# Timer Event 
#----------------------------------------
TME_INT = 0x00000001            # Event that interval is satisfied
#----------------------------------------
# Analog Input Status
#----------------------------------------
AIS_BUSY = 0x00000001           # Device is working
AIS_START_TRG = 0x00000002      # Wait the start trigger
AIS_DATA_NUM = 0x00000010       # Store the data of the specified number of samplings
AIS_OFERR = 0x00010000          # Overflow
AIS_SCERR = 0x00020000          # Sampling clock error
AIS_AIERR = 0x00040000          # AD converting error
AIS_DRVERR = 0x00080000         # Driver spec error
#----------------------------------------
# Analog Output Status
#----------------------------------------
AOS_BUSY = 0x00000001           # Device is working
AOS_START_TRG = 0x00000002      # Wait the start trigger
AOS_DATA_NUM = 0x00000010       # Output the data of the specified number of samplings
AOS_SCERR = 0x00020000          # Sampling clock error
AOS_AOERR = 0x00040000          # DA converting error
AOS_DRVERR = 0x00080000         # Driver spec error
#----------------------------------------
# Counter Status 
#----------------------------------------
CNTS_BUSY = 0x00000001          # Counter is working
CNTS_DATA_NUM = 0x00000010      # Count comparison match
CNTS_ORERR = 0x00010000         # Overrun
CNTS_ERR = 0x00020000           # Count operating error
#----------------------------------------
# Analog Input Message
#----------------------------------------
AIOM_AIE_START = 0x1000         # Event that AD converting start condition are satisfied
AIOM_AIE_RPTEND = 0x1001        # Event of repeat end
AIOM_AIE_END = 0x1002           # Event of device operation end
AIOM_AIE_DATA_NUM = 0x1003      # Event that data of the specified sampling times are stored
AIOM_AIE_DATA_TSF = 0x1007      # Event that data of the specified number are transferred
AIOM_AIE_OFERR = 0x1004         # Event of Overflow
AIOM_AIE_SCERR = 0x1005         # Event of sampling clock error
AIOM_AIE_ADERR = 0x1006         # Event of AD converting error
#----------------------------------------
# Analog Output Message
#----------------------------------------
AIOM_AOE_START = 0x1020         # Event that DA converting start conditions are satisfied
AIOM_AOE_RPTEND = 0x1021        # Event of repeat end
AIOM_AOE_END = 0x1022           # Event of device operation end
AIOM_AOE_DATA_NUM = 0x1023      # Event that data of the specified sampling times are output
AIOM_AOE_DATA_TSF = 0x1027      # Event that data of the specified number are transferred
AIOM_AOE_SCERR = 0x1025         # Event of sampling clock error
AIOM_AOE_DAERR = 0x1026         # Event of DA converting error
#----------------------------------------
# Counter Message
#----------------------------------------
AIOM_CNTE_DATA_NUM = 0x1042     # Event of count comparison match
AIOM_CNTE_ORERR = 0x1043        # Event of count overrun
AIOM_CNTE_ERR = 0x1044          # Event of counter operating error
#----------------------------------------
# Timer Message
#----------------------------------------
AIOM_TME_INT = 0x1060           # Event that interval is satisfied
#----------------------------------------
# Analog Input Attached Data
#----------------------------------------
AIAT_AI = 0x00000001            # Analog input attached information
AIAT_AO0 = 0x00000100           # Analong output data
AIAT_DIO0 = 0x00010000          # Digital input and output data
AIAT_CNT0 = 0x01000000          # Data of counter channel 0
AIAT_CNT1 = 0x02000000          # Data of counter channel 1
#----------------------------------------
# Counter Action Mode
#----------------------------------------
CNT_LOADPRESET = 0x0000001      # Load the preset count value
CNT_LOADCOMP = 0x0000002        # Load the count comparison value
#----------------------------------------
# Event Controller Destination Signal
#----------------------------------------
AIOECU_DEST_AI_CLK = 4          # Analog input sampling clock
AIOECU_DEST_AI_START = 0        # Analog input converting start signal
AIOECU_DEST_AI_STOP = 2         # Analog input converting stop signal
AIOECU_DEST_AO_CLK = 36         # Analog output sampling clock
AIOECU_DEST_AO_START = 32       # Analog output converting start signal
AIOECU_DEST_AO_STOP = 34        # Analog output converting stop signal
AIOECU_DEST_CNT0_UPCLK = 134    # Up clock signal of counter 0
AIOECU_DEST_CNT1_UPCLK = 135    # Up clock signal of counter 1
AIOECU_DEST_CNT0_START = 128    # Start signal of counter 0, timer 0
AIOECU_DEST_CNT1_START = 129    # Start signal of counter 1, timer 1
AIOECU_DEST_CNT0_STOP = 130     # Stop signal of counter 0, timer 0
AIOECU_DEST_CNT1_STOP = 131     # Stop signal of counter 1, timer 1
AIOECU_DEST_MASTER1 = 104       # Synchronization bus master signal 1
AIOECU_DEST_MASTER2 = 105       # Synchronization bus master signal 2
AIOECU_DEST_MASTER3 = 106       # Synchronization bus master signal 3
#----------------------------------------
# Event Controller Source Signal
#----------------------------------------
AIOECU_SRC_OPEN = -1            # Not connect
AIOECU_SRC_AI_CLK = 4           # Analog input internal clock signal
AIOECU_SRC_AI_EXTCLK = 146      # Analog input external clock signal
AIOECU_SRC_AI_TRGSTART = 144    # Analog input external trigger start signal
AIOECU_SRC_AI_LVSTART = 28      # Analog input level trigger start signal
AIOECU_SRC_AI_STOP = 17         # Analog input signal that data of the specified sampling times have been converted (No delay)
AIOECU_SRC_AI_STOP_DELAY = 18   # Analog input signal that data of the specified sampling times have been converted (delay)
AIOECU_SRC_AI_LVSTOP = 29       # Analog input level trigger stop signal
AIOECU_SRC_AI_TRGSTOP = 145     # Analog input external trigger stop signal
AIOECU_SRC_AO_CLK = 66          # Analog output internal clock signal
AIOECU_SRC_AO_EXTCLK = 149      # Analog output external clock signal
AIOECU_SRC_AO_TRGSTART = 147    # Analog output external trigger start signal
AIOECU_SRC_AO_STOP_FIFO = 352   # Analog output signal that data of the specified sampling times have been output (FIFO)
AIOECU_SRC_AO_STOP_RING = 80    # Analog output signal that data of the specified sampling times have been output (RING)
AIOECU_SRC_AO_TRGSTOP = 148     # Analog output external trigger stop signal
AIOECU_SRC_CNT0_UPCLK = 150     # Up clock signal of counter 0
AIOECU_SRC_CNT1_UPCLK = 152     # Up clock signal of counter 1
AIOECU_SRC_CNT0_CMP = 288       # Count comparison match of counter 0
AIOECU_SRC_CNT1_CMP = 289       # Count comparison match of counter 1
AIOECU_SRC_SLAVE1 = 136         # Synchronization bus master signal 1
AIOECU_SRC_SLAVE2 = 137         # Synchronization bus master signal 2
AIOECU_SRC_SLAVE3 = 138         # Synchronization bus master signal 3
AIOECU_SRC_START = 384          # Ai, Ao, Cnt, Tm software start signal
AIOECU_SRC_STOP = 385           # Ai, Ao, Cnt, Tm software stop signal
#----------------------------------------
# M Device Counter Message
#----------------------------------------
AIOM_CNTM_COUNTUP_CH0 = 0x1070      # COUNTUP, CHANNEL No.0
AIOM_CNTM_COUNTUP_CH1 = 0x1071      # COUNTUP, CHANNEL No.1
AIOM_CNTM_TIME_UP = 0x1090          # Timer
AIOM_CNTM_COUNTER_ERROR = 0x1091    # Counter error
AIOM_CNTM_CARRY_BORROW = 0x1092     # Carry/Borrow


#----------------------------------------
# Types for callback function.
#----------------------------------------
PAIO_AI_CALLBACK = ctypes.WINFUNCTYPE(None,
                                       ctypes.c_short, ctypes.c_short, ctypes.wintypes.WPARAM,
                                       ctypes.wintypes.LPARAM, ctypes.c_void_p)
PAIO_AO_CALLBACK = ctypes.WINFUNCTYPE(None,
                                       ctypes.c_short, ctypes.c_short, ctypes.wintypes.WPARAM,
                                       ctypes.wintypes.LPARAM, ctypes.c_void_p)
PAIO_CNT_CALLBACK = ctypes.WINFUNCTYPE(None,
                                       ctypes.c_short, ctypes.c_short, ctypes.wintypes.WPARAM,
                                       ctypes.wintypes.LPARAM, ctypes.c_void_p)
PAIO_TM_CALLBACK = ctypes.WINFUNCTYPE(None,
                                       ctypes.c_short, ctypes.c_short, ctypes.wintypes.WPARAM,
                                       ctypes.wintypes.LPARAM, ctypes.c_void_p)
PAIO_MATCH_CALLBACK = ctypes.WINFUNCTYPE(None,
                                       ctypes.c_short,  ctypes.wintypes.WPARAM,
                                       ctypes.wintypes.LPARAM, ctypes.c_void_p)
PAIO_TIMEUP_CALLBACK = ctypes.WINFUNCTYPE(None,
                                       ctypes.c_short,  ctypes.wintypes.WPARAM,
                                       ctypes.wintypes.LPARAM, ctypes.c_void_p)
PAIO_COUNTER_ERR_CALLBACK = ctypes.WINFUNCTYPE(None,
                                            ctypes.c_short,  ctypes.wintypes.WPARAM,
                                            ctypes.wintypes.LPARAM, ctypes.c_void_p)
PAIO_CARRY_BORROW_CALLBACK = ctypes.WINFUNCTYPE(None,
                                           ctypes.c_short,  ctypes.wintypes.WPARAM,
                                           ctypes.wintypes.LPARAM, ctypes.c_void_p)


#----------------------------------------
# Prototype definition
#----------------------------------------
#----------------------------------------
# Common function
#----------------------------------------
# C Prototype: long WINAPI AioInit(char * DeviceName, short * Id);
AioInit = caio_dll.AioInit
AioInit.restype = ctypes.c_long
AioInit.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_short)]

# C Prototype: long WINAPI AioExit(short Id);
AioExit = caio_dll.AioExit
AioExit.restype = ctypes.c_long
AioExit.argtypes = [ctypes.c_short]

# C Prototype: long WINAPI AioResetDevice(short Id);
AioResetDevice = caio_dll.AioResetDevice
AioResetDevice.restype = ctypes.c_long
AioResetDevice.argtypes = [ctypes.c_short]

# C Prototype: long WINAPI AioGetErrorString(long ErrorCode, char * ErrorString);
AioGetErrorString = caio_dll.AioGetErrorString
AioGetErrorString.restype = ctypes.c_long
AioGetErrorString.argtypes = [ctypes.c_long, ctypes.c_char_p]

# C Prototype: long WINAPI AioQueryDeviceName(short Index, char * DeviceName, char * Device);
AioQueryDeviceName = caio_dll.AioQueryDeviceName
AioQueryDeviceName.restype = ctypes.c_long
AioQueryDeviceName.argtypes = [ctypes.c_short, ctypes.c_char_p, ctypes.c_char_p]

# C Prototype: long WINAPI AioGetDeviceType(char * Device, short * DeviceType);
AioGetDeviceType = caio_dll.AioGetDeviceType
AioGetDeviceType.restype = ctypes.c_long
AioGetDeviceType.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_short)]

# C Prototype: long WINAPI AioSetControlFilter(short Id, short Signal, float Value);
AioSetControlFilter = caio_dll.AioSetControlFilter
AioSetControlFilter.restype = ctypes.c_long
AioSetControlFilter.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_float]

# C Prototype: long WINAPI AioGetControlFilter(short Id, short Signal, float *Value);
AioGetControlFilter = caio_dll.AioGetControlFilter
AioGetControlFilter.restype = ctypes.c_long
AioGetControlFilter.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.c_float)]

# C Prototype: long WINAPI AioResetProcess(short Id);
AioResetProcess = caio_dll.AioResetProcess
AioResetProcess.restype = ctypes.c_long
AioResetProcess.argtypes = [ctypes.c_short]

#----------------------------------------
# Analog input function
#----------------------------------------
# C Prototype: long WINAPI AioSingleAi(short Id, short AiChannel, long * AiData);
AioSingleAi = caio_dll.AioSingleAi
AioSingleAi.restype = ctypes.c_long
AioSingleAi.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.c_long)]

# C Prototype: long WINAPI AioSingleAiEx(short Id, short AiChannel, float * AiData);
AioSingleAiEx = caio_dll.AioSingleAiEx
AioSingleAiEx.restype = ctypes.c_long
AioSingleAiEx.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.c_float)]

# C Prototype: long WINAPI AioMultiAi(short Id, short AiChannels, long * AiData);
AioMultiAi = caio_dll.AioMultiAi
AioMultiAi.restype = ctypes.c_long
AioMultiAi.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.c_long)]

# C Prototype: long WINAPI AioMultiAiEx(short Id, short AiChannels, float * AiData);
AioMultiAiEx = caio_dll.AioMultiAiEx
AioMultiAiEx.restype = ctypes.c_long
AioMultiAiEx.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.c_float)]

# C Prototype: long WINAPI AioSingleAiSR(short Id, short AiChannel, long * AiData, unsigned short * Timestamp, BYTE Mode);
AioSingleAiSR = caio_dll.AioSingleAiSR
AioSingleAiSR.restype = ctypes.c_long
AioSingleAiSR.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.c_long), ctypes.POINTER(ctypes.c_ushort), ctypes.c_ubyte]

# C Prototype: long WINAPI AioSingleAiExSR(short Id, short AiChannel, float * AiData, unsigned short * Timestamp, BYTE Mode);
AioSingleAiExSR = caio_dll.AioSingleAiExSR
AioSingleAiExSR.restype = ctypes.c_long
AioSingleAiExSR.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_ushort), ctypes.c_ubyte]

# C Prototype: long WINAPI AioMultiAiSR(short Id, short AiChannels, long * AiData, unsigned short * Timestamp, BYTE Mode);
AioMultiAiSR = caio_dll.AioMultiAiSR
AioMultiAiSR.restype = ctypes.c_long
AioMultiAiSR.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.c_long), ctypes.POINTER(ctypes.c_ushort), ctypes.c_ubyte]

# C Prototype: long WINAPI AioMultiAiExSR(short Id, short AiChannels, float * AiData, unsigned short * Timestamp, BYTE Mode);
AioMultiAiExSR = caio_dll.AioMultiAiExSR
AioMultiAiExSR.restype = ctypes.c_long
AioMultiAiExSR.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_ushort), ctypes.c_ubyte]

# C Prototype: long WINAPI AioGetAiResolution(short Id, short * AiResolution);
AioGetAiResolution = caio_dll.AioGetAiResolution
AioGetAiResolution.restype = ctypes.c_long
AioGetAiResolution.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_short)]

# C Prototype: long WINAPI AioSetAiInputMethod(short Id, short AiInputMethod);
AioSetAiInputMethod = caio_dll.AioSetAiInputMethod
AioSetAiInputMethod.restype = ctypes.c_long
AioSetAiInputMethod.argtypes = [ctypes.c_short, ctypes.c_short]

# C Prototype: long WINAPI AioGetAiInputMethod(short Id, short * AiInputMethod);
AioGetAiInputMethod = caio_dll.AioGetAiInputMethod
AioGetAiInputMethod.restype = ctypes.c_long
AioGetAiInputMethod.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_short)]

# C Prototype: long WINAPI AioGetAiMaxChannels(short Id, short * AiMaxChannels);
AioGetAiMaxChannels = caio_dll.AioGetAiMaxChannels
AioGetAiMaxChannels.restype = ctypes.c_long
AioGetAiMaxChannels.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_short)]

# C Prototype: long WINAPI AioSetAiChannel(short Id, short AiChannel, short Enabled);
AioSetAiChannel = caio_dll.AioSetAiChannel
AioSetAiChannel.restype = ctypes.c_long
AioSetAiChannel.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_short]

# C Prototype: long WINAPI AioGetAiChannel(short Id, short AiChannel, short *Enabled);
AioGetAiChannel = caio_dll.AioGetAiChannel
AioGetAiChannel.restype = ctypes.c_long
AioGetAiChannel.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.c_short)]

# C Prototype: long WINAPI AioSetAiChannels(short Id, short AiChannels);
AioSetAiChannels = caio_dll.AioSetAiChannels
AioSetAiChannels.restype = ctypes.c_long
AioSetAiChannels.argtypes = [ctypes.c_short, ctypes.c_short]

# C Prototype: long WINAPI AioGetAiChannels(short Id, short * AiChannels);
AioGetAiChannels = caio_dll.AioGetAiChannels
AioGetAiChannels.restype = ctypes.c_long
AioGetAiChannels.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_short)]

# C Prototype: long WINAPI AioSetAiChannelSequence(short Id, short AiSequence, short AiChannel);
AioSetAiChannelSequence = caio_dll.AioSetAiChannelSequence
AioSetAiChannelSequence.restype = ctypes.c_long
AioSetAiChannelSequence.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_short]

# C Prototype: long WINAPI AioGetAiChannelSequence(short Id, short AiSequence, short * AiChannel);
AioGetAiChannelSequence = caio_dll.AioGetAiChannelSequence
AioGetAiChannelSequence.restype = ctypes.c_long
AioGetAiChannelSequence.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.c_short)]

# C Prototype: long WINAPI AioSetAiRange(short Id, short AiChannel, short AiRange);
AioSetAiRange = caio_dll.AioSetAiRange
AioSetAiRange.restype = ctypes.c_long
AioSetAiRange.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_short]

# C Prototype: long WINAPI AioSetAiRangeAll(short Id, short AiRange);
AioSetAiRangeAll = caio_dll.AioSetAiRangeAll
AioSetAiRangeAll.restype = ctypes.c_long
AioSetAiRangeAll.argtypes = [ctypes.c_short, ctypes.c_short]

# C Prototype: long WINAPI AioGetAiRange(short Id, short AiChannel, short * AiRange);
AioGetAiRange = caio_dll.AioGetAiRange
AioGetAiRange.restype = ctypes.c_long
AioGetAiRange.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.c_short)]

# C Prototype: long WINAPI AioSetAiTransferMode(short Id, short AiTransferMode);
AioSetAiTransferMode = caio_dll.AioSetAiTransferMode
AioSetAiTransferMode.restype = ctypes.c_long
AioSetAiTransferMode.argtypes = [ctypes.c_short, ctypes.c_short]

# C Prototype: long WINAPI AioGetAiTransferMode(short Id, short *AiTransferMode);
AioGetAiTransferMode = caio_dll.AioGetAiTransferMode
AioGetAiTransferMode.restype = ctypes.c_long
AioGetAiTransferMode.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_short)]

# C Prototype: long WINAPI AioSetAiDeviceBufferMode(short Id, short AiDeviceBufferMode);
AioSetAiDeviceBufferMode = caio_dll.AioSetAiDeviceBufferMode
AioSetAiDeviceBufferMode.restype = ctypes.c_long
AioSetAiDeviceBufferMode.argtypes = [ctypes.c_short, ctypes.c_short]

# C Prototype: long WINAPI AioGetAiDeviceBufferMode(short Id, short *AiDeviceBufferMode);
AioGetAiDeviceBufferMode = caio_dll.AioGetAiDeviceBufferMode
AioGetAiDeviceBufferMode.restype = ctypes.c_long
AioGetAiDeviceBufferMode.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_short)]

# C Prototype: long WINAPI AioSetAiMemorySize(short Id, long AiMemorySize);
AioSetAiMemorySize = caio_dll.AioSetAiMemorySize
AioSetAiMemorySize.restype = ctypes.c_long
AioSetAiMemorySize.argtypes = [ctypes.c_short, ctypes.c_long]

# C Prototype: long WINAPI AioGetAiMemorySize(short Id, long *AiMemorySize);
AioGetAiMemorySize = caio_dll.AioGetAiMemorySize
AioGetAiMemorySize.restype = ctypes.c_long
AioGetAiMemorySize.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_long)]

# C Prototype: long WINAPI AioSetAiTransferData(short Id, long DataNumber, long *Buffer);
AioSetAiTransferData = caio_dll.AioSetAiTransferData
AioSetAiTransferData.restype = ctypes.c_long
AioSetAiTransferData.argtypes = [ctypes.c_short, ctypes.c_long, ctypes.POINTER(ctypes.c_long)]

# C Prototype: long WINAPI AioSetAiAttachedData(short Id, long AttachedData);
AioSetAiAttachedData = caio_dll.AioSetAiAttachedData
AioSetAiAttachedData.restype = ctypes.c_long
AioSetAiAttachedData.argtypes = [ctypes.c_short, ctypes.c_long]

# C Prototype: long WINAPI AioGetAiSamplingDataSize(short Id, short *DataSize);
AioGetAiSamplingDataSize = caio_dll.AioGetAiSamplingDataSize
AioGetAiSamplingDataSize.restype = ctypes.c_long
AioGetAiSamplingDataSize.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_short)]

# C Prototype: long WINAPI AioSetAiMemoryType(short Id, short AiMemoryType);
AioSetAiMemoryType = caio_dll.AioSetAiMemoryType
AioSetAiMemoryType.restype = ctypes.c_long
AioSetAiMemoryType.argtypes = [ctypes.c_short, ctypes.c_short]

# C Prototype: long WINAPI AioGetAiMemoryType(short Id, short * AiMemoryType);
AioGetAiMemoryType = caio_dll.AioGetAiMemoryType
AioGetAiMemoryType.restype = ctypes.c_long
AioGetAiMemoryType.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_short)]

# C Prototype: long WINAPI AioSetAiRepeatTimes(short Id, long AiRepeatTimes);
AioSetAiRepeatTimes = caio_dll.AioSetAiRepeatTimes
AioSetAiRepeatTimes.restype = ctypes.c_long
AioSetAiRepeatTimes.argtypes = [ctypes.c_short, ctypes.c_long]

# C Prototype: long WINAPI AioGetAiRepeatTimes(short Id, long * AiRepeatTimes);
AioGetAiRepeatTimes = caio_dll.AioGetAiRepeatTimes
AioGetAiRepeatTimes.restype = ctypes.c_long
AioGetAiRepeatTimes.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_long)]

# C Prototype: long WINAPI AioSetAiClockType(short Id, short AiClockType);
AioSetAiClockType = caio_dll.AioSetAiClockType
AioSetAiClockType.restype = ctypes.c_long
AioSetAiClockType.argtypes = [ctypes.c_short, ctypes.c_short]

# C Prototype: long WINAPI AioGetAiClockType(short Id, short * AiClockType);
AioGetAiClockType = caio_dll.AioGetAiClockType
AioGetAiClockType.restype = ctypes.c_long
AioGetAiClockType.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_short)]

# C Prototype: long WINAPI AioSetAiSamplingClock(short Id, float AiSamplingClock);
AioSetAiSamplingClock = caio_dll.AioSetAiSamplingClock
AioSetAiSamplingClock.restype = ctypes.c_long
AioSetAiSamplingClock.argtypes = [ctypes.c_short, ctypes.c_float]

# C Prototype: long WINAPI AioGetAiSamplingClock(short Id, float * AiSamplingClock);
AioGetAiSamplingClock = caio_dll.AioGetAiSamplingClock
AioGetAiSamplingClock.restype = ctypes.c_long
AioGetAiSamplingClock.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_float)]

# C Prototype: long WINAPI AioSetAiScanClock(short Id, float AiScanClock);
AioSetAiScanClock = caio_dll.AioSetAiScanClock
AioSetAiScanClock.restype = ctypes.c_long
AioSetAiScanClock.argtypes = [ctypes.c_short, ctypes.c_float]

# C Prototype: long WINAPI AioGetAiScanClock(short Id, float * AiScanClock);
AioGetAiScanClock = caio_dll.AioGetAiScanClock
AioGetAiScanClock.restype = ctypes.c_long
AioGetAiScanClock.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_float)]

# C Prototype: long WINAPI AioSetAiClockEdge(short Id, short AoClockEdge);
AioSetAiClockEdge = caio_dll.AioSetAiClockEdge
AioSetAiClockEdge.restype = ctypes.c_long
AioSetAiClockEdge.argtypes = [ctypes.c_short, ctypes.c_short]

# C Prototype: long WINAPI AioGetAiClockEdge(short Id, short * AoClockEdge);
AioGetAiClockEdge = caio_dll.AioGetAiClockEdge
AioGetAiClockEdge.restype = ctypes.c_long
AioGetAiClockEdge.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_short)]

# C Prototype: long WINAPI AioSetAiStartTrigger(short Id, short AiStartTrigger);
AioSetAiStartTrigger = caio_dll.AioSetAiStartTrigger
AioSetAiStartTrigger.restype = ctypes.c_long
AioSetAiStartTrigger.argtypes = [ctypes.c_short, ctypes.c_short]

# C Prototype: long WINAPI AioGetAiStartTrigger(short Id, short * AiStartTrigger);
AioGetAiStartTrigger = caio_dll.AioGetAiStartTrigger
AioGetAiStartTrigger.restype = ctypes.c_long
AioGetAiStartTrigger.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_short)]

# C Prototype: long WINAPI AioSetAiStartLevel(short Id, short AiChannel, long AiStartLevel, short AiDirection);
AioSetAiStartLevel = caio_dll.AioSetAiStartLevel
AioSetAiStartLevel.restype = ctypes.c_long
AioSetAiStartLevel.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_long, ctypes.c_short]

# C Prototype: long WINAPI AioSetAiStartLevelEx(short Id, short AiChannel, float AiStartLevel, short AiDirection);
AioSetAiStartLevelEx = caio_dll.AioSetAiStartLevelEx
AioSetAiStartLevelEx.restype = ctypes.c_long
AioSetAiStartLevelEx.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_float, ctypes.c_short]

# C Prototype: long WINAPI AioGetAiStartLevel(short Id, short AiChannel, long * AiStartLevel, short * AiDirection);
AioGetAiStartLevel = caio_dll.AioGetAiStartLevel
AioGetAiStartLevel.restype = ctypes.c_long
AioGetAiStartLevel.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.c_long), ctypes.POINTER(ctypes.c_short)]

# C Prototype: long WINAPI AioGetAiStartLevelEx(short Id, short AiChannel, float * AiStartLevel, short * AiDirection);
AioGetAiStartLevelEx = caio_dll.AioGetAiStartLevelEx
AioGetAiStartLevelEx.restype = ctypes.c_long
AioGetAiStartLevelEx.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_short)]

# C Prototype: long WINAPI AioSetAiStartInRange(short Id, short AiChannel, long Level1, long Level2, long StateTimes);
AioSetAiStartInRange = caio_dll.AioSetAiStartInRange
AioSetAiStartInRange.restype = ctypes.c_long
AioSetAiStartInRange.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_long, ctypes.c_long, ctypes.c_long]

# C Prototype: long WINAPI AioSetAiStartInRangeEx(short Id, short AiChannel, float Level1, float Level2, long StateTimes);
AioSetAiStartInRangeEx = caio_dll.AioSetAiStartInRangeEx
AioSetAiStartInRangeEx.restype = ctypes.c_long
AioSetAiStartInRangeEx.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_float, ctypes.c_float, ctypes.c_long]

# C Prototype: long WINAPI AioGetAiStartInRange(short Id, short AiChannel, long *Level1, long *Level2, long *StateTimes);
AioGetAiStartInRange = caio_dll.AioGetAiStartInRange
AioGetAiStartInRange.restype = ctypes.c_long
AioGetAiStartInRange.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.c_long), ctypes.POINTER(ctypes.c_long), ctypes.POINTER(ctypes.c_long)]

# C Prototype: long WINAPI AioGetAiStartInRangeEx(short Id, short AiChannel, float *Level1, float *Level2, long *StateTimes);
AioGetAiStartInRangeEx = caio_dll.AioGetAiStartInRangeEx
AioGetAiStartInRangeEx.restype = ctypes.c_long
AioGetAiStartInRangeEx.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_long)]

# C Prototype: long WINAPI AioSetAiStartOutRange(short Id, short AiChannel, long Level1, long Level2, long StateTimes);
AioSetAiStartOutRange = caio_dll.AioSetAiStartOutRange
AioSetAiStartOutRange.restype = ctypes.c_long
AioSetAiStartOutRange.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_long, ctypes.c_long, ctypes.c_long]

# C Prototype: long WINAPI AioSetAiStartOutRangeEx(short Id, short AiChannel, float Level1, float Level2, long StateTimes);
AioSetAiStartOutRangeEx = caio_dll.AioSetAiStartOutRangeEx
AioSetAiStartOutRangeEx.restype = ctypes.c_long
AioSetAiStartOutRangeEx.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_float, ctypes.c_float, ctypes.c_long]

# C Prototype: long WINAPI AioGetAiStartOutRange(short Id, short AiChannel, long *Level1, long *Level2, long *StateTimes);
AioGetAiStartOutRange = caio_dll.AioGetAiStartOutRange
AioGetAiStartOutRange.restype = ctypes.c_long
AioGetAiStartOutRange.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.c_long), ctypes.POINTER(ctypes.c_long), ctypes.POINTER(ctypes.c_long)]

# C Prototype: long WINAPI AioGetAiStartOutRangeEx(short Id, short AiChannel, float *Level1, float *Level2, long *StateTimes);
AioGetAiStartOutRangeEx = caio_dll.AioGetAiStartOutRangeEx
AioGetAiStartOutRangeEx.restype = ctypes.c_long
AioGetAiStartOutRangeEx.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_long)]

# C Prototype: long WINAPI AioSetAiStopTrigger(short Id, short AiStopTrigger);
AioSetAiStopTrigger = caio_dll.AioSetAiStopTrigger
AioSetAiStopTrigger.restype = ctypes.c_long
AioSetAiStopTrigger.argtypes = [ctypes.c_short, ctypes.c_short]

# C Prototype: long WINAPI AioGetAiStopTrigger(short Id, short * AiStopTrigger);
AioGetAiStopTrigger = caio_dll.AioGetAiStopTrigger
AioGetAiStopTrigger.restype = ctypes.c_long
AioGetAiStopTrigger.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_short)]

# C Prototype: long WINAPI AioSetAiStopTimes(short Id, long AiStopTimes);
AioSetAiStopTimes = caio_dll.AioSetAiStopTimes
AioSetAiStopTimes.restype = ctypes.c_long
AioSetAiStopTimes.argtypes = [ctypes.c_short, ctypes.c_long]

# C Prototype: long WINAPI AioGetAiStopTimes(short Id, long * AiStopTimes);
AioGetAiStopTimes = caio_dll.AioGetAiStopTimes
AioGetAiStopTimes.restype = ctypes.c_long
AioGetAiStopTimes.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_long)]

# C Prototype: long WINAPI AioSetAiStopLevel(short Id, short AiChannel, long AiStopLevel, short AiDirection);
AioSetAiStopLevel = caio_dll.AioSetAiStopLevel
AioSetAiStopLevel.restype = ctypes.c_long
AioSetAiStopLevel.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_long, ctypes.c_short]

# C Prototype: long WINAPI AioSetAiStopLevelEx(short Id, short AiChannel, float AiStopLevel, short AiDirection);
AioSetAiStopLevelEx = caio_dll.AioSetAiStopLevelEx
AioSetAiStopLevelEx.restype = ctypes.c_long
AioSetAiStopLevelEx.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_float, ctypes.c_short]

# C Prototype: long WINAPI AioGetAiStopLevel(short Id, short AiChannel, long * AiStopLevel, short * AiDirection);
AioGetAiStopLevel = caio_dll.AioGetAiStopLevel
AioGetAiStopLevel.restype = ctypes.c_long
AioGetAiStopLevel.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.c_long), ctypes.POINTER(ctypes.c_short)]

# C Prototype: long WINAPI AioGetAiStopLevelEx(short Id, short AiChannel, float * AiStopLevel, short * AiDirection);
AioGetAiStopLevelEx = caio_dll.AioGetAiStopLevelEx
AioGetAiStopLevelEx.restype = ctypes.c_long
AioGetAiStopLevelEx.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_short)]

# C Prototype: long WINAPI AioSetAiStopInRange(short Id, short AiChannel, long Level1, long Level2, long StateTimes);
AioSetAiStopInRange = caio_dll.AioSetAiStopInRange
AioSetAiStopInRange.restype = ctypes.c_long
AioSetAiStopInRange.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_long, ctypes.c_long, ctypes.c_long]

# C Prototype: long WINAPI AioSetAiStopInRangeEx(short Id, short AiChannel, float Level1, float Level2, long StateTimes);
AioSetAiStopInRangeEx = caio_dll.AioSetAiStopInRangeEx
AioSetAiStopInRangeEx.restype = ctypes.c_long
AioSetAiStopInRangeEx.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_float, ctypes.c_float, ctypes.c_long]

# C Prototype: long WINAPI AioGetAiStopInRange(short Id, short AiChannel, long *Level1, long *Level2, long *StateTimes);
AioGetAiStopInRange = caio_dll.AioGetAiStopInRange
AioGetAiStopInRange.restype = ctypes.c_long
AioGetAiStopInRange.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.c_long), ctypes.POINTER(ctypes.c_long), ctypes.POINTER(ctypes.c_long)]

# C Prototype: long WINAPI AioGetAiStopInRangeEx(short Id, short AiChannel, float *Level1, float *Level2, long *StateTimes);
AioGetAiStopInRangeEx = caio_dll.AioGetAiStopInRangeEx
AioGetAiStopInRangeEx.restype = ctypes.c_long
AioGetAiStopInRangeEx.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_long)]

# C Prototype: long WINAPI AioSetAiStopOutRange(short Id, short AiChannel, long Level1, long Level2, long StateTimes);
AioSetAiStopOutRange = caio_dll.AioSetAiStopOutRange
AioSetAiStopOutRange.restype = ctypes.c_long
AioSetAiStopOutRange.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_long, ctypes.c_long, ctypes.c_long]

# C Prototype: long WINAPI AioSetAiStopOutRangeEx(short Id, short AiChannel, float Level1, float Level2, long StateTimes);
AioSetAiStopOutRangeEx = caio_dll.AioSetAiStopOutRangeEx
AioSetAiStopOutRangeEx.restype = ctypes.c_long
AioSetAiStopOutRangeEx.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_float, ctypes.c_float, ctypes.c_long]

# C Prototype: long WINAPI AioGetAiStopOutRange(short Id, short AiChannel, long *Level1, long *Level2, long *StateTimes);
AioGetAiStopOutRange = caio_dll.AioGetAiStopOutRange
AioGetAiStopOutRange.restype = ctypes.c_long
AioGetAiStopOutRange.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.c_long), ctypes.POINTER(ctypes.c_long), ctypes.POINTER(ctypes.c_long)]

# C Prototype: long WINAPI AioGetAiStopOutRangeEx(short Id, short AiChannel, float *Level1, float *Level2, long *StateTimes);
AioGetAiStopOutRangeEx = caio_dll.AioGetAiStopOutRangeEx
AioGetAiStopOutRangeEx.restype = ctypes.c_long
AioGetAiStopOutRangeEx.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_long)]

# C Prototype: long WINAPI AioSetAiStopDelayTimes(short Id, long AiStopDelayTimes);
AioSetAiStopDelayTimes = caio_dll.AioSetAiStopDelayTimes
AioSetAiStopDelayTimes.restype = ctypes.c_long
AioSetAiStopDelayTimes.argtypes = [ctypes.c_short, ctypes.c_long]

# C Prototype: long WINAPI AioGetAiStopDelayTimes(short Id, long * AiStopDelayTimes);
AioGetAiStopDelayTimes = caio_dll.AioGetAiStopDelayTimes
AioGetAiStopDelayTimes.restype = ctypes.c_long
AioGetAiStopDelayTimes.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_long)]

# C Prototype: long WINAPI AioSetAiEvent(short Id, HWND hWnd, long AiEvent);
AioSetAiEvent = caio_dll.AioSetAiEvent
AioSetAiEvent.restype = ctypes.c_long
AioSetAiEvent.argtypes = [ctypes.c_short, ctypes.wintypes.HANDLE, ctypes.c_long]

# C Prototype: long WINAPI AioGetAiEvent(short Id, HWND * hWnd, long * AiEvent);
AioGetAiEvent = caio_dll.AioGetAiEvent
AioGetAiEvent.restype = ctypes.c_long
AioGetAiEvent.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.wintypes.HANDLE), ctypes.POINTER(ctypes.c_long)]

# C Prototype: long WINAPI AioSetAiCallBackProc(short Id,
#                                               long (_stdcall *pProc)(short Id, short AiEvent, WPARAM wParam, LPARAM lParam, void *Param), long AiEvent, void *Param);
AioSetAiCallBackProc = caio_dll.AioSetAiCallBackProc
AioSetAiCallBackProc.restype = ctypes.c_long
AioSetAiCallBackProc.argtypes = [ctypes.c_short, PAIO_AI_CALLBACK, ctypes.c_long, ctypes.c_void_p]

# C Prototype: long WINAPI AioSetAiEventSamplingTimes(short Id, long AiSamplingTimes);
AioSetAiEventSamplingTimes = caio_dll.AioSetAiEventSamplingTimes
AioSetAiEventSamplingTimes.restype = ctypes.c_long
AioSetAiEventSamplingTimes.argtypes = [ctypes.c_short, ctypes.c_long]

# C Prototype: long WINAPI AioGetAiEventSamplingTimes(short Id, long * AiSamplingTimes);
AioGetAiEventSamplingTimes = caio_dll.AioGetAiEventSamplingTimes
AioGetAiEventSamplingTimes.restype = ctypes.c_long
AioGetAiEventSamplingTimes.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_long)]

# C Prototype: long WINAPI AioSetAiEventTransferTimes(short Id, long AiTransferTimes);
AioSetAiEventTransferTimes = caio_dll.AioSetAiEventTransferTimes
AioSetAiEventTransferTimes.restype = ctypes.c_long
AioSetAiEventTransferTimes.argtypes = [ctypes.c_short, ctypes.c_long]

# C Prototype: long WINAPI AioGetAiEventTransferTimes(short Id, long *AiTransferTimes);
AioGetAiEventTransferTimes = caio_dll.AioGetAiEventTransferTimes
AioGetAiEventTransferTimes.restype = ctypes.c_long
AioGetAiEventTransferTimes.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_long)]

# C Prototype: long WINAPI AioStartAi(short Id);
AioStartAi = caio_dll.AioStartAi
AioStartAi.restype = ctypes.c_long
AioStartAi.argtypes = [ctypes.c_short]

# C Prototype: long WINAPI AioStartAiSync(short Id, long TimeOut);
AioStartAiSync = caio_dll.AioStartAiSync
AioStartAiSync.restype = ctypes.c_long
AioStartAiSync.argtypes = [ctypes.c_short, ctypes.c_long]

# C Prototype: long WINAPI AioStopAi(short Id);
AioStopAi = caio_dll.AioStopAi
AioStopAi.restype = ctypes.c_long
AioStopAi.argtypes = [ctypes.c_short]

# C Prototype: long WINAPI AioGetAiStatus(short Id, long * AiStatus);
AioGetAiStatus = caio_dll.AioGetAiStatus
AioGetAiStatus.restype = ctypes.c_long
AioGetAiStatus.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_long)]

# C Prototype: long WINAPI AioGetAiSamplingCount(short Id, long * AiSamplingCount);
AioGetAiSamplingCount = caio_dll.AioGetAiSamplingCount
AioGetAiSamplingCount.restype = ctypes.c_long
AioGetAiSamplingCount.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_long)]

# C Prototype: long WINAPI AioGetAiStopTriggerCount(short Id, long * AiStopTriggerCount);
AioGetAiStopTriggerCount = caio_dll.AioGetAiStopTriggerCount
AioGetAiStopTriggerCount.restype = ctypes.c_long
AioGetAiStopTriggerCount.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_long)]

# C Prototype: long WINAPI AioGetAiTransferCount(short Id, long *AiTransferCount);
AioGetAiTransferCount = caio_dll.AioGetAiTransferCount
AioGetAiTransferCount.restype = ctypes.c_long
AioGetAiTransferCount.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_long)]

# C Prototype: long WINAPI AioGetAiTransferLap(short Id, long *Lap);
AioGetAiTransferLap = caio_dll.AioGetAiTransferLap
AioGetAiTransferLap.restype = ctypes.c_long
AioGetAiTransferLap.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_long)]

# C Prototype: long WINAPI AioGetAiStopTriggerTransferCount(short Id, long *Count);
AioGetAiStopTriggerTransferCount = caio_dll.AioGetAiStopTriggerTransferCount
AioGetAiStopTriggerTransferCount.restype = ctypes.c_long
AioGetAiStopTriggerTransferCount.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_long)]

# C Prototype: long WINAPI AioGetAiRepeatCount(short Id, long * AiRepeatCount);
AioGetAiRepeatCount = caio_dll.AioGetAiRepeatCount
AioGetAiRepeatCount.restype = ctypes.c_long
AioGetAiRepeatCount.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_long)]

# C Prototype: long WINAPI AioGetAiSamplingData(short Id, long * AiSamplingTimes, long * AiData);
AioGetAiSamplingData = caio_dll.AioGetAiSamplingData
AioGetAiSamplingData.restype = ctypes.c_long
AioGetAiSamplingData.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_long), ctypes.POINTER(ctypes.c_long)]

# C Prototype: long WINAPI AioGetAiSamplingDataEx(short Id, long * AiSamplingTimes, float * AiData);
AioGetAiSamplingDataEx = caio_dll.AioGetAiSamplingDataEx
AioGetAiSamplingDataEx.restype = ctypes.c_long
AioGetAiSamplingDataEx.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_long), ctypes.POINTER(ctypes.c_float)]

# C Prototype: long WINAPI AioResetAiStatus(short Id);
AioResetAiStatus = caio_dll.AioResetAiStatus
AioResetAiStatus.restype = ctypes.c_long
AioResetAiStatus.argtypes = [ctypes.c_short]

# C Prototype: long WINAPI AioResetAiMemory(short Id);
AioResetAiMemory = caio_dll.AioResetAiMemory
AioResetAiMemory.restype = ctypes.c_long
AioResetAiMemory.argtypes = [ctypes.c_short]

# C Prototype: AioSetAiDigitalFilter(short Id, short AiChannel, short FilterType, short FilterValue);
AioSetAiDigitalFilter = caio_dll.AioSetAiDigitalFilter
AioSetAiDigitalFilter.restype = ctypes.c_long
AioSetAiDigitalFilter.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_short, ctypes.c_short]

# C Prototype: AioGetAiDigitalFilter(short Id, short AiChannel, short *FilterType, short *FilterValue);
AioGetAiDigitalFilter = caio_dll.AioGetAiDigitalFilter
AioGetAiDigitalFilter.restype = ctypes.c_long
AioGetAiDigitalFilter.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.c_short), ctypes.POINTER(ctypes.c_short)]

#----------------------------------------
# Analog output function
#----------------------------------------
# C Prototype: long WINAPI AioSingleAo(short Id, short AoChannel, long AoData);
AioSingleAo = caio_dll.AioSingleAo
AioSingleAo.restype = ctypes.c_long
AioSingleAo.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_long]

# C Prototype: long WINAPI AioSingleAoEx(short Id, short AoChannel, float AoData);
AioSingleAoEx = caio_dll.AioSingleAoEx
AioSingleAoEx.restype = ctypes.c_long
AioSingleAoEx.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_float]

# C Prototype: long WINAPI AioMultiAo(short Id, short AoChannels, long * AoData);
AioMultiAo = caio_dll.AioMultiAo
AioMultiAo.restype = ctypes.c_long
AioMultiAo.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.c_long)]

# C Prototype: long WINAPI AioMultiAoEx(short Id, short AoChannels, float * AoData);
AioMultiAoEx = caio_dll.AioMultiAoEx
AioMultiAoEx.restype = ctypes.c_long
AioMultiAoEx.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.c_float)]

# C Prototype: long WINAPI AioGetAoResolution(short Id, short * AoResolution);
AioGetAoResolution = caio_dll.AioGetAoResolution
AioGetAoResolution.restype = ctypes.c_long
AioGetAoResolution.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_short)]

# C Prototype: long WINAPI AioSetAoChannels(short Id, short AoChannels);
AioSetAoChannels = caio_dll.AioSetAoChannels
AioSetAoChannels.restype = ctypes.c_long
AioSetAoChannels.argtypes = [ctypes.c_short, ctypes.c_short]

# C Prototype: long WINAPI AioGetAoChannels(short Id, short * AoChannels);
AioGetAoChannels = caio_dll.AioGetAoChannels
AioGetAoChannels.restype = ctypes.c_long
AioGetAoChannels.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_short)]

# C Prototype: long WINAPI AioGetAoMaxChannels(short Id, short * AoMaxChannels);
AioGetAoMaxChannels = caio_dll.AioGetAoMaxChannels
AioGetAoMaxChannels.restype = ctypes.c_long
AioGetAoMaxChannels.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_short)]

# C Prototype: long WINAPI AioSetAoRange(short Id, short AoChannel, short AoRange);
AioSetAoRange = caio_dll.AioSetAoRange
AioSetAoRange.restype = ctypes.c_long
AioSetAoRange.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_short]

# C Prototype: long WINAPI AioSetAoRangeAll(short Id, short AoRange);
AioSetAoRangeAll = caio_dll.AioSetAoRangeAll
AioSetAoRangeAll.restype = ctypes.c_long
AioSetAoRangeAll.argtypes = [ctypes.c_short, ctypes.c_short]

# C Prototype: long WINAPI AioGetAoRange(short Id, short AoChannel, short * AoRange);
AioGetAoRange = caio_dll.AioGetAoRange
AioGetAoRange.restype = ctypes.c_long
AioGetAoRange.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.c_short)]

# C Prototype: long WINAPI AioSetAoTransferMode(short Id, short AoTransferMode);
AioSetAoTransferMode = caio_dll.AioSetAoTransferMode
AioSetAoTransferMode.restype = ctypes.c_long
AioSetAoTransferMode.argtypes = [ctypes.c_short, ctypes.c_short]

# C Prototype: long WINAPI AioGetAoTransferMode(short Id, short *AoTransferMode);
AioGetAoTransferMode = caio_dll.AioGetAoTransferMode
AioGetAoTransferMode.restype = ctypes.c_long
AioGetAoTransferMode.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_short)]

# C Prototype: long WINAPI AioSetAoDeviceBufferMode(short Id, short AoDeviceBufferMode);
AioSetAoDeviceBufferMode = caio_dll.AioSetAoDeviceBufferMode
AioSetAoDeviceBufferMode.restype = ctypes.c_long
AioSetAoDeviceBufferMode.argtypes = [ctypes.c_short, ctypes.c_short]

# C Prototype: long WINAPI AioGetAoDeviceBufferMode(short Id, short *AoDeviceBufferMode);
AioGetAoDeviceBufferMode = caio_dll.AioGetAoDeviceBufferMode
AioGetAoDeviceBufferMode.restype = ctypes.c_long
AioGetAoDeviceBufferMode.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_short)]

# C Prototype: long WINAPI AioSetAoMemorySize(short Id, long AoMemorySize);
AioSetAoMemorySize = caio_dll.AioSetAoMemorySize
AioSetAoMemorySize.restype = ctypes.c_long
AioSetAoMemorySize.argtypes = [ctypes.c_short, ctypes.c_long]

# C Prototype: long WINAPI AioGetAoMemorySize(short Id, long *AoMemorySize);
AioGetAoMemorySize = caio_dll.AioGetAoMemorySize
AioGetAoMemorySize.restype = ctypes.c_long
AioGetAoMemorySize.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_long)]

# C Prototype: long WINAPI AioSetAoTransferData(short Id, long DataNumber, long *Buffer);
AioSetAoTransferData = caio_dll.AioSetAoTransferData
AioSetAoTransferData.restype = ctypes.c_long
AioSetAoTransferData.argtypes = [ctypes.c_short, ctypes.c_long, ctypes.POINTER(ctypes.c_long)]

# C Prototype: long WINAPI AioGetAoSamplingDataSize(short Id, short *DataSize);
AioGetAoSamplingDataSize = caio_dll.AioGetAoSamplingDataSize
AioGetAoSamplingDataSize.restype = ctypes.c_long
AioGetAoSamplingDataSize.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_short)]

# C Prototype: long WINAPI AioSetAoMemoryType(short Id, short AoMemoryType);
AioSetAoMemoryType = caio_dll.AioSetAoMemoryType
AioSetAoMemoryType.restype = ctypes.c_long
AioSetAoMemoryType.argtypes = [ctypes.c_short, ctypes.c_short]

# C Prototype: long WINAPI AioGetAoMemoryType(short Id, short * AoMemoryType);
AioGetAoMemoryType = caio_dll.AioGetAoMemoryType
AioGetAoMemoryType.restype = ctypes.c_long
AioGetAoMemoryType.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_short)]

# C Prototype: long WINAPI AioSetAoRepeatTimes(short Id, long AoRepeatTimes);
AioSetAoRepeatTimes = caio_dll.AioSetAoRepeatTimes
AioSetAoRepeatTimes.restype = ctypes.c_long
AioSetAoRepeatTimes.argtypes = [ctypes.c_short, ctypes.c_long]

# C Prototype: long WINAPI AioGetAoRepeatTimes(short Id, long * AoRepeatTimes);
AioGetAoRepeatTimes = caio_dll.AioGetAoRepeatTimes
AioGetAoRepeatTimes.restype = ctypes.c_long
AioGetAoRepeatTimes.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_long)]

# C Prototype: long WINAPI AioSetAoClockType(short Id, short AoClockType);
AioSetAoClockType = caio_dll.AioSetAoClockType
AioSetAoClockType.restype = ctypes.c_long
AioSetAoClockType.argtypes = [ctypes.c_short, ctypes.c_short]

# C Prototype: long WINAPI AioGetAoClockType(short Id, short * AoClockType);
AioGetAoClockType = caio_dll.AioGetAoClockType
AioGetAoClockType.restype = ctypes.c_long
AioGetAoClockType.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_short)]

# C Prototype: long WINAPI AioSetAoSamplingClock(short Id, float AoSamplingClock);
AioSetAoSamplingClock = caio_dll.AioSetAoSamplingClock
AioSetAoSamplingClock.restype = ctypes.c_long
AioSetAoSamplingClock.argtypes = [ctypes.c_short, ctypes.c_float]

# C Prototype: long WINAPI AioGetAoSamplingClock(short Id, float * AoSamplingClock);
AioGetAoSamplingClock = caio_dll.AioGetAoSamplingClock
AioGetAoSamplingClock.restype = ctypes.c_long
AioGetAoSamplingClock.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_float)]

# C Prototype: long WINAPI AioSetAoClockEdge(short Id, short AoClockEdge);
AioSetAoClockEdge = caio_dll.AioSetAoClockEdge
AioSetAoClockEdge.restype = ctypes.c_long
AioSetAoClockEdge.argtypes = [ctypes.c_short, ctypes.c_short]

# C Prototype: long WINAPI AioGetAoClockEdge(short Id, short * AoClockEdge);
AioGetAoClockEdge = caio_dll.AioGetAoClockEdge
AioGetAoClockEdge.restype = ctypes.c_long
AioGetAoClockEdge.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_short)]

# C Prototype: long WINAPI AioSetAoSamplingData(short Id, long AoSamplingTimes, long * AoData);
AioSetAoSamplingData = caio_dll.AioSetAoSamplingData
AioSetAoSamplingData.restype = ctypes.c_long
AioSetAoSamplingData.argtypes = [ctypes.c_short, ctypes.c_long, ctypes.POINTER(ctypes.c_long)]

# C Prototype: long WINAPI AioSetAoSamplingDataEx(short Id, long AoSamplingTimes, float * AoData);
AioSetAoSamplingDataEx = caio_dll.AioSetAoSamplingDataEx
AioSetAoSamplingDataEx.restype = ctypes.c_long
AioSetAoSamplingDataEx.argtypes = [ctypes.c_short, ctypes.c_long, ctypes.POINTER(ctypes.c_float)]

# C Prototype: long WINAPI AioGetAoSamplingTimes(short Id, long * AoSamplingTimes);
AioGetAoSamplingTimes = caio_dll.AioGetAoSamplingTimes
AioGetAoSamplingTimes.restype = ctypes.c_long
AioGetAoSamplingTimes.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_long)]

# C Prototype: long WINAPI AioSetAoStartTrigger(short Id, short AoStartTrigger);
AioSetAoStartTrigger = caio_dll.AioSetAoStartTrigger
AioSetAoStartTrigger.restype = ctypes.c_long
AioSetAoStartTrigger.argtypes = [ctypes.c_short, ctypes.c_short]

# C Prototype: long WINAPI AioGetAoStartTrigger(short Id, short * AoStartTrigger);
AioGetAoStartTrigger = caio_dll.AioGetAoStartTrigger
AioGetAoStartTrigger.restype = ctypes.c_long
AioGetAoStartTrigger.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_short)]

# C Prototype: long WINAPI AioSetAoStopTrigger(short Id, short AoStopTrigger);
AioSetAoStopTrigger = caio_dll.AioSetAoStopTrigger
AioSetAoStopTrigger.restype = ctypes.c_long
AioSetAoStopTrigger.argtypes = [ctypes.c_short, ctypes.c_short]

# C Prototype: long WINAPI AioGetAoStopTrigger(short Id, short * AoStopTrigger);
AioGetAoStopTrigger = caio_dll.AioGetAoStopTrigger
AioGetAoStopTrigger.restype = ctypes.c_long
AioGetAoStopTrigger.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_short)]

# C Prototype: long WINAPI AioSetAoEvent(short Id, HWND hWnd, long AoEvent);
AioSetAoEvent = caio_dll.AioSetAoEvent
AioSetAoEvent.restype = ctypes.c_long
AioSetAoEvent.argtypes = [ctypes.c_short, ctypes.wintypes.HANDLE, ctypes.c_long]

# C Prototype: long WINAPI AioGetAoEvent(short Id, HWND * hWnd, long * AoEvent);
AioGetAoEvent = caio_dll.AioGetAoEvent
AioGetAoEvent.restype = ctypes.c_long
AioGetAoEvent.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.wintypes.HANDLE), ctypes.POINTER(ctypes.c_long)]

# C Prototype: long WINAPI AioSetAoCallBackProc(short Id,
#                                               long (_stdcall *pProc)(short Id, short AiEvent, WPARAM wParam, LPARAM lParam, void *Param), long AoEvent, void *Param);
AioSetAoCallBackProc = caio_dll.AioSetAoCallBackProc
AioSetAoCallBackProc.restype = ctypes.c_long
AioSetAoCallBackProc.argtypes = [ctypes.c_short, PAIO_AO_CALLBACK, ctypes.c_long, ctypes.c_void_p]

# C Prototype: long WINAPI AioSetAoEventSamplingTimes(short Id, long AoSamplingTimes);
AioSetAoEventSamplingTimes = caio_dll.AioSetAoEventSamplingTimes
AioSetAoEventSamplingTimes.restype = ctypes.c_long
AioSetAoEventSamplingTimes.argtypes = [ctypes.c_short, ctypes.c_long]

# C Prototype: long WINAPI AioGetAoEventSamplingTimes(short Id, long * AoSamplingTimes);
AioGetAoEventSamplingTimes = caio_dll.AioGetAoEventSamplingTimes
AioGetAoEventSamplingTimes.restype = ctypes.c_long
AioGetAoEventSamplingTimes.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_long)]

# C Prototype: long WINAPI AioSetAoEventTransferTimes(short Id, long AoTransferTimes);
AioSetAoEventTransferTimes = caio_dll.AioSetAoEventTransferTimes
AioSetAoEventTransferTimes.restype = ctypes.c_long
AioSetAoEventTransferTimes.argtypes = [ctypes.c_short, ctypes.c_long]

# C Prototype: long WINAPI AioGetAoEventTransferTimes(short Id, long *AoTransferTimes);
AioGetAoEventTransferTimes = caio_dll.AioGetAoEventTransferTimes
AioGetAoEventTransferTimes.restype = ctypes.c_long
AioGetAoEventTransferTimes.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_long)]

# C Prototype: long WINAPI AioStartAo(short Id);
AioStartAo = caio_dll.AioStartAo
AioStartAo.restype = ctypes.c_long
AioStartAo.argtypes = [ctypes.c_short]

# C Prototype: long WINAPI AioStopAo(short Id);
AioStopAo = caio_dll.AioStopAo
AioStopAo.restype = ctypes.c_long
AioStopAo.argtypes = [ctypes.c_short]

# C Prototype: long WINAPI AioEnableAo(short Id, short AoChannel);
AioEnableAo = caio_dll.AioEnableAo
AioEnableAo.restype = ctypes.c_long
AioEnableAo.argtypes = [ctypes.c_short, ctypes.c_short]

# C Prototype: long WINAPI AioDisableAo(short Id, short AoChannel);
AioDisableAo = caio_dll.AioDisableAo
AioDisableAo.restype = ctypes.c_long
AioDisableAo.argtypes = [ctypes.c_short, ctypes.c_short]

# C Prototype: long WINAPI AioGetAoStatus(short Id, long * AoStatus);
AioGetAoStatus = caio_dll.AioGetAoStatus
AioGetAoStatus.restype = ctypes.c_long
AioGetAoStatus.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_long)]

# C Prototype: long WINAPI AioGetAoSamplingCount(short Id, long * AoSamplingCount);
AioGetAoSamplingCount = caio_dll.AioGetAoSamplingCount
AioGetAoSamplingCount.restype = ctypes.c_long
AioGetAoSamplingCount.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_long)]

# C Prototype: long WINAPI AioGetAoTransferCount(short Id, long *AoTransferCount);
AioGetAoTransferCount = caio_dll.AioGetAoTransferCount
AioGetAoTransferCount.restype = ctypes.c_long
AioGetAoTransferCount.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_long)]

# C Prototype: long WINAPI AioGetAoTransferLap(short Id, long *Lap);
AioGetAoTransferLap = caio_dll.AioGetAoTransferLap
AioGetAoTransferLap.restype = ctypes.c_long
AioGetAoTransferLap.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_long)]

# C Prototype: long WINAPI AioGetAoRepeatCount(short Id, long * AoRepeatCount);
AioGetAoRepeatCount = caio_dll.AioGetAoRepeatCount
AioGetAoRepeatCount.restype = ctypes.c_long
AioGetAoRepeatCount.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_long)]

# C Prototype: long WINAPI AioResetAoStatus(short Id);
AioResetAoStatus = caio_dll.AioResetAoStatus
AioResetAoStatus.restype = ctypes.c_long
AioResetAoStatus.argtypes = [ctypes.c_short]

# C Prototype: long WINAPI AioResetAoMemory(short Id);
AioResetAoMemory = caio_dll.AioResetAoMemory
AioResetAoMemory.restype = ctypes.c_long
AioResetAoMemory.argtypes = [ctypes.c_short]


#----------------------------------------
# Digital input and output function
#----------------------------------------
# C Prototype: long WINAPI AioSetDiFilter(short Id, short Bit, float Value);
AioSetDiFilter = caio_dll.AioSetDiFilter
AioSetDiFilter.restype = ctypes.c_long
AioSetDiFilter.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_float]

# C Prototype: long WINAPI AioGetDiFilter(short Id, short Bit, float *Value);
AioGetDiFilter = caio_dll.AioGetDiFilter
AioGetDiFilter.restype = ctypes.c_long
AioGetDiFilter.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.c_float)]

# C Prototype: long WINAPI AioInputDiBit(short Id, short DiBit, short * DiData);
AioInputDiBit = caio_dll.AioInputDiBit
AioInputDiBit.restype = ctypes.c_long
AioInputDiBit.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.c_short)]

# C Prototype: long WINAPI AioOutputDoBit(short Id, short DoBit, short DoData);
AioOutputDoBit = caio_dll.AioOutputDoBit
AioOutputDoBit.restype = ctypes.c_long
AioOutputDoBit.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_short]

# C Prototype: long WINAPI AioInputDiByte(short Id, short DiPort, short * DiData);
AioInputDiByte = caio_dll.AioInputDiByte
AioInputDiByte.restype = ctypes.c_long
AioInputDiByte.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.c_short)]

# C Prototype: long WINAPI AioOutputDoByte(short Id, short DoPort, short DoData);
AioOutputDoByte = caio_dll.AioOutputDoByte
AioOutputDoByte.restype = ctypes.c_long
AioOutputDoByte.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_short]

# C Prototype: long WINAPI AioSetDioDirection(short Id, long Dir);
AioSetDioDirection = caio_dll.AioSetDioDirection
AioSetDioDirection.restype = ctypes.c_long
AioSetDioDirection.argtypes = [ctypes.c_short, ctypes.c_long]

# C Prototype: long WINAPI AioGetDioDirection (short Id, long * Dir);
AioGetDioDirection = caio_dll.AioGetDioDirection
AioGetDioDirection.restype = ctypes.c_long
AioGetDioDirection.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_long)]


#----------------------------------------
# Counter function
#----------------------------------------
# C Prototype: long WINAPI AioGetCntMaxChannels(short Id, short * CntMaxChannels);
AioGetCntMaxChannels = caio_dll.AioGetCntMaxChannels
AioGetCntMaxChannels.restype = ctypes.c_long
AioGetCntMaxChannels.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_short)]

# C Prototype: long WINAPI AioSetCntComparisonMode(short Id, short CntChannel, short CntMode);
AioSetCntComparisonMode = caio_dll.AioSetCntComparisonMode
AioSetCntComparisonMode.restype = ctypes.c_long
AioSetCntComparisonMode.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_short]

# C Prototype: long WINAPI AioGetCntComparisonMode(short Id, short CntChannel, short *CntMode);
AioGetCntComparisonMode = caio_dll.AioGetCntComparisonMode
AioGetCntComparisonMode.restype = ctypes.c_long
AioGetCntComparisonMode.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.c_short)]

# C Prototype: long WINAPI AioSetCntPresetReg(short Id, short CntChannel, long PresetNumber, long *PresetData, short Flag);
AioSetCntPresetReg = caio_dll.AioSetCntPresetReg
AioSetCntPresetReg.restype = ctypes.c_long
AioSetCntPresetReg.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_long, ctypes.POINTER(ctypes.c_long), ctypes.c_short]

# C Prototype: long WINAPI AioSetCntComparisonReg(short Id, short CntChannel, long ComparisonNumber, long *ComparisonData, short Flag);
AioSetCntComparisonReg = caio_dll.AioSetCntComparisonReg
AioSetCntComparisonReg.restype = ctypes.c_long
AioSetCntComparisonReg.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_long, ctypes.POINTER(ctypes.c_long), ctypes.c_short]

# C Prototype: long WINAPI AioSetCntInputSignal(short Id, short CntChannel, short CntInputSignal);
AioSetCntInputSignal = caio_dll.AioSetCntInputSignal
AioSetCntInputSignal.restype = ctypes.c_long
AioSetCntInputSignal.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_short]

# C Prototype: long WINAPI AioGetCntInputSignal(short Id, short CntChannel, short *CntInputSignal);
AioGetCntInputSignal = caio_dll.AioGetCntInputSignal
AioGetCntInputSignal.restype = ctypes.c_long
AioGetCntInputSignal.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.c_short)]

# C Prototype: long WINAPI AioSetCntEvent(short Id, short CntChannel, HWND hWnd, long CntEvent);
AioSetCntEvent = caio_dll.AioSetCntEvent
AioSetCntEvent.restype = ctypes.c_long
AioSetCntEvent.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.wintypes.HANDLE, ctypes.c_long]

# C Prototype: long WINAPI AioGetCntEvent(short Id, short CntChannel, HWND *hWnd, long *CntEvent);
AioGetCntEvent = caio_dll.AioGetCntEvent
AioGetCntEvent.restype = ctypes.c_long
AioGetCntEvent.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.wintypes.HANDLE), ctypes.POINTER(ctypes.c_long)]

# C Prototype: long WINAPI AioSetCntCallBackProc(short Id, short CntChannel,
#                                               long (_stdcall *pProc)(short Id, short CntEvent, WPARAM wParam, LPARAM lParam, void *Param), long CntEvent, void *Param);
AioSetCntCallBackProc = caio_dll.AioSetCntCallBackProc
AioSetCntCallBackProc.restype = ctypes.c_long
AioSetCntCallBackProc.argtypes = [ctypes.c_short, ctypes.c_short, PAIO_CNT_CALLBACK, ctypes.c_long, ctypes.c_void_p]

# C Prototype: long WINAPI AioSetCntFilter(short Id, short CntChannel, short Signal, float Value);
AioSetCntFilter = caio_dll.AioSetCntFilter
AioSetCntFilter.restype = ctypes.c_long
AioSetCntFilter.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_short, ctypes.c_float]

# C Prototype: long WINAPI AioGetCntFilter(short Id, short CntChannel, short Signal, float *Value);
AioGetCntFilter = caio_dll.AioGetCntFilter
AioGetCntFilter.restype = ctypes.c_long
AioGetCntFilter.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.c_float)]

# C Prototype: long WINAPI AioStartCnt(short Id, short CntChannel);
AioStartCnt = caio_dll.AioStartCnt
AioStartCnt.restype = ctypes.c_long
AioStartCnt.argtypes = [ctypes.c_short, ctypes.c_short]

# C Prototype: long WINAPI AioStopCnt(short Id, short CntChannel);
AioStopCnt = caio_dll.AioStopCnt
AioStopCnt.restype = ctypes.c_long
AioStopCnt.argtypes = [ctypes.c_short, ctypes.c_short]

# C Prototype: long WINAPI AioPresetCnt(short Id, short CntChannel, long PresetData);
AioPresetCnt = caio_dll.AioPresetCnt
AioPresetCnt.restype = ctypes.c_long
AioPresetCnt.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_long]

# C Prototype: long WINAPI AioGetCntStatus(short Id, short CntChannel, long *CntStatus);
AioGetCntStatus = caio_dll.AioGetCntStatus
AioGetCntStatus.restype = ctypes.c_long
AioGetCntStatus.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.c_long)]

# C Prototype: long WINAPI AioGetCntCount(short Id, short CntChannel, long *Count);
AioGetCntCount = caio_dll.AioGetCntCount
AioGetCntCount.restype = ctypes.c_long
AioGetCntCount.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.c_long)]

# C Prototype: long WINAPI AioResetCntStatus(short Id, short CntChannel, long CntStatus);
AioResetCntStatus = caio_dll.AioResetCntStatus
AioResetCntStatus.restype = ctypes.c_long
AioResetCntStatus.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_long]


#----------------------------------------
# Timer function
#----------------------------------------
# C Prototype: long WINAPI AioSetTmEvent(short Id, short TimerId, HWND hWnd, long TmEvent);
AioSetTmEvent = caio_dll.AioSetTmEvent
AioSetTmEvent.restype = ctypes.c_long
AioSetTmEvent.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.wintypes.HANDLE, ctypes.c_long]

# C Prototype: long WINAPI AioGetTmEvent(short Id, short TimerId, HWND * hWnd, long * TmEvent);
AioGetTmEvent = caio_dll.AioGetTmEvent
AioGetTmEvent.restype = ctypes.c_long
AioGetTmEvent.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.wintypes.HANDLE), ctypes.POINTER(ctypes.c_long)]

# C Prototype: long WINAPI AioSetTmCallBackProc(short Id, short TimerId,
#                                               long (_stdcall *pProc)(short Id, short TmEvent, WPARAM wParam, LPARAM lParam, void *Param), long TmEvent, void *Param);
AioSetTmCallBackProc = caio_dll.AioSetTmCallBackProc
AioSetTmCallBackProc.restype = ctypes.c_long
AioSetTmCallBackProc.argtypes = [ctypes.c_short, ctypes.c_short, PAIO_TM_CALLBACK, ctypes.c_long, ctypes.c_void_p]

# C Prototype: long WINAPI AioStartTmTimer(short Id, short TimerId, float Interval);
AioStartTmTimer = caio_dll.AioStartTmTimer
AioStartTmTimer.restype = ctypes.c_long
AioStartTmTimer.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_float]

# C Prototype: long WINAPI AioStopTmTimer(short Id, short TimerId);
AioStopTmTimer = caio_dll.AioStopTmTimer
AioStopTmTimer.restype = ctypes.c_long
AioStopTmTimer.argtypes = [ctypes.c_short, ctypes.c_short]

# C Prototype: long WINAPI AioStartTmCount(short Id, short TimerId);
AioStartTmCount = caio_dll.AioStartTmCount
AioStartTmCount.restype = ctypes.c_long
AioStartTmCount.argtypes = [ctypes.c_short, ctypes.c_short]

# C Prototype: long WINAPI AioStopTmCount(short Id, short TimerId);
AioStopTmCount = caio_dll.AioStopTmCount
AioStopTmCount.restype = ctypes.c_long
AioStopTmCount.argtypes = [ctypes.c_short, ctypes.c_short]

# C Prototype: long WINAPI AioLapTmCount(short Id, short TimerId, long *Lap);
AioLapTmCount = caio_dll.AioLapTmCount
AioLapTmCount.restype = ctypes.c_long
AioLapTmCount.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.c_long)]

# C Prototype: long WINAPI AioResetTmCount(short Id, short TimerId);
AioResetTmCount = caio_dll.AioResetTmCount
AioResetTmCount.restype = ctypes.c_long
AioResetTmCount.argtypes = [ctypes.c_short, ctypes.c_short]

# C Prototype: long WINAPI AioTmWait(short Id, short TimerId, long Wait);
AioTmWait = caio_dll.AioTmWait
AioTmWait.restype = ctypes.c_long
AioTmWait.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_long]


#----------------------------------------
# Event Controller
#----------------------------------------
# C Prototype: long WINAPI AioSetEcuSignal(short Id, short Destination, short Source);
AioSetEcuSignal = caio_dll.AioSetEcuSignal
AioSetEcuSignal.restype = ctypes.c_long
AioSetEcuSignal.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_short]

# C Prototype: long WINAPI AioGetEcuSignal(short Id, short Destination, short *Source);
AioGetEcuSignal = caio_dll.AioGetEcuSignal
AioGetEcuSignal.restype = ctypes.c_long
AioGetEcuSignal.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.c_short)]


""" End of support for AIO-121601M-PCI
#----------------------------------------
# AIO-121601-M-PCI dedicated function
#----------------------------------------
#----------------------------------------
# Setting function (set)
#----------------------------------------
# C Prototype: long WINAPI AioGetCntmMaxChannels(short Id, short *CntmMaxChannels);
AioGetCntmMaxChannels = caio_dll.AioGetCntmMaxChannels
AioGetCntmMaxChannels.restype = ctypes.c_long
AioGetCntmMaxChannels.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_short)]

# C Prototype: long WINAPI AioSetCntmZMode(short Id, short ChNo, short Mode);
AioSetCntmZMode = caio_dll.AioSetCntmZMode
AioSetCntmZMode.restype = ctypes.c_long
AioSetCntmZMode.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_short]

# C Prototype: long WINAPI AioSetCntmZLogic(short Id, short ChNo, short ZLogic);
AioSetCntmZLogic = caio_dll.AioSetCntmZLogic
AioSetCntmZLogic.restype = ctypes.c_long
AioSetCntmZLogic.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.c_short)]

# C Prototype: long WINAPI AioSelectCntmChannelSignal(short Id, short ChNo, short Mode);
AioSelectCntmChannelSignal = caio_dll.AioSelectCntmChannelSignal
AioSelectCntmChannelSignal.restype = ctypes.c_long
AioSelectCntmChannelSignal.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_short]

# C Prototype: long WINAPI AioSetCntmCountDirection(short Id, short ChNo, short Dir);
AioSetCntmCountDirection = caio_dll.AioSetCntmCountDirection
AioSetCntmCountDirection.restype = ctypes.c_long
AioSetCntmCountDirection.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_short]

# C Prototype: long WINAPI AioSetCntmOperationMode(short Id, short ChNo, short Phase, short Mul, short SyncClr);
AioSetCntmOperationMode = caio_dll.AioSetCntmOperationMode
AioSetCntmOperationMode.restype = ctypes.c_long
AioSetCntmOperationMode.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_short, ctypes.c_short, ctypes.c_short]

# C Prototype: long WINAPI AioSetCntmDigitalFilter(short Id, short ChNo, short FilterValue);
AioSetCntmDigitalFilter = caio_dll.AioSetCntmDigitalFilter
AioSetCntmDigitalFilter.restype = ctypes.c_long
AioSetCntmDigitalFilter.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_short]

# C Prototype: long WINAPI AioSetCntmPulseWidth(short Id, short ChNo, short PlsWidth);
AioSetCntmPulseWidth = caio_dll.AioSetCntmPulseWidth
AioSetCntmPulseWidth.restype = ctypes.c_long
AioSetCntmPulseWidth.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_short]

# C Prototype: long WINAPI AioSetCntmDIType(short Id, short ChNo, short InputType);
AioSetCntmDIType = caio_dll.AioSetCntmDIType
AioSetCntmDIType.restype = ctypes.c_long
AioSetCntmDIType.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_short]

# C Prototype: long WINAPI AioSetCntmOutputHardwareEvent(short Id, short ChNo, short OutputLogic, unsigned long EventType, short PulseWidth);
AioSetCntmOutputHardwareEvent = caio_dll.AioSetCntmOutputHardwareEvent
AioSetCntmOutputHardwareEvent.restype = ctypes.c_long
AioSetCntmOutputHardwareEvent.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_short, ctypes.c_ulong, ctypes.c_short]

# C Prototype: long WINAPI AioSetCntmInputHardwareEvent(short Id, short ChNo, unsigned long EventType, short RF0, short RF1, short Reserved);
AioSetCntmInputHardwareEvent = caio_dll.AioSetCntmInputHardwareEvent
AioSetCntmInputHardwareEvent.restype = ctypes.c_long
AioSetCntmInputHardwareEvent.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_ulong, ctypes.c_short, ctypes.c_short, ctypes.c_short]

# C Prototype: long WINAPI AioSetCntmCountMatchHardwareEvent(short Id, short ChNo, short RegisterNo, unsigned long EventType, short Reserved);
AioSetCntmCountMatchHardwareEvent = caio_dll.AioSetCntmCountMatchHardwareEvent
AioSetCntmCountMatchHardwareEvent.restype = ctypes.c_long
AioSetCntmCountMatchHardwareEvent.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_short, ctypes.c_ulong, ctypes.c_short]

# C Prototype: long WINAPI AioSetCntmPresetRegister(short Id, short ChNo, unsigned long PresetData, short Reserved);
AioSetCntmPresetRegister = caio_dll.AioSetCntmPresetRegister
AioSetCntmPresetRegister.restype = ctypes.c_long
AioSetCntmPresetRegister.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_ulong, ctypes.c_short]

# C Prototype: long WINAPI AioSetCntmTestPulse(short Id, short CntmInternal, short CntmOut, short CntmReserved);
AioSetCntmTestPulse = caio_dll.AioSetCntmTestPulse
AioSetCntmTestPulse.restype = ctypes.c_long
AioSetCntmTestPulse.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_short, ctypes.c_short]


#----------------------------------------
# Setting function (get)
#----------------------------------------
# C Prototype: long WINAPI AioGetCntmZMode(short Id, short ChNo, short *Mode);
AioGetCntmZMode = caio_dll.AioGetCntmZMode
AioGetCntmZMode.restype = ctypes.c_long
AioGetCntmZMode.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.c_short)]

# C Prototype: long WINAPI AioGetCntmZLogic(short Id, short ChNo, short *ZLogic);
AioGetCntmZLogic = caio_dll.AioGetCntmZLogic
AioGetCntmZLogic.restype = ctypes.c_long
AioGetCntmZLogic.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.c_short)]

# C Prototype: long WINAPI AioGetCntmChannelSignal(short Id, short CntmChNo, short *CntmSigType);
AioGetCntmChannelSignal = caio_dll.AioGetCntmChannelSignal
AioGetCntmChannelSignal.restype = ctypes.c_long
AioGetCntmChannelSignal.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.c_short)]

# C Prototype: long WINAPI AioGetCntmCountDirection(short Id, short ChNo, short *Dir);
AioGetCntmCountDirection = caio_dll.AioGetCntmCountDirection
AioGetCntmCountDirection.restype = ctypes.c_long
AioGetCntmCountDirection.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.c_short)]

# C Prototype: long WINAPI AioGetCntmOperationMode(short Id, short ChNo, short *Phase, short *Mul, short *SyncClr);
AioGetCntmOperationMode = caio_dll.AioGetCntmOperationMode
AioGetCntmOperationMode.restype = ctypes.c_long
AioGetCntmOperationMode.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.c_short), ctypes.POINTER(ctypes.c_short), ctypes.POINTER(ctypes.c_short)]

# C Prototype: long WINAPI AioGetCntmDigitalFilter(short Id, short ChNo, short *FilterValue);
AioGetCntmDigitalFilter = caio_dll.AioGetCntmDigitalFilter
AioGetCntmDigitalFilter.restype = ctypes.c_long
AioGetCntmDigitalFilter.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.c_short)]

# C Prototype: long WINAPI AioGetCntmPulseWidth(short Id, short ChNo, short *PlsWidth);
AioGetCntmPulseWidth = caio_dll.AioGetCntmPulseWidth
AioGetCntmPulseWidth.restype = ctypes.c_long
AioGetCntmPulseWidth.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.c_short)]


#----------------------------------------
# Counter function
#----------------------------------------
# C Prototype: long WINAPI AioCntmStartCount(short Id, short *ChNo, short ChNum);
AioCntmStartCount = caio_dll.AioCntmStartCount
AioCntmStartCount.restype = ctypes.c_long
AioCntmStartCount.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_short), ctypes.c_short]

# C Prototype: long WINAPI AioCntmStopCount(short Id, short *ChNo, short ChNum);
AioCntmStopCount = caio_dll.AioCntmStopCount
AioCntmStopCount.restype = ctypes.c_long
AioCntmStopCount.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_short), ctypes.c_short]

# C Prototype: long WINAPI AioCntmPreset(short Id, short *ChNo, short ChNum, unsigned long *PresetData);
AioCntmPreset = caio_dll.AioCntmPreset
AioCntmPreset.restype = ctypes.c_long
AioCntmPreset.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_short), ctypes.c_short, ctypes.POINTER(ctypes.c_ulong)]

# C Prototype: long WINAPI AioCntmZeroClearCount(short Id, short *ChNo, short ChNum);
AioCntmZeroClearCount = caio_dll.AioCntmZeroClearCount
AioCntmZeroClearCount.restype = ctypes.c_long
AioCntmZeroClearCount.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_short), ctypes.c_short]

# C Prototype: long WINAPI AioCntmReadCount(short Id, short *ChNo, short ChNum, unsigned long *CntDat);
AioCntmReadCount = caio_dll.AioCntmReadCount
AioCntmReadCount.restype = ctypes.c_long
AioCntmReadCount.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_short), ctypes.c_short, ctypes.POINTER(ctypes.c_ulong)]

# C Prototype: long WINAPI AioCntmReadStatus(short Id, short ChNo, short *Sts);
AioCntmReadStatus = caio_dll.AioCntmReadStatus
AioCntmReadStatus.restype = ctypes.c_long
AioCntmReadStatus.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.c_short)]

# C Prototype: long WINAPI AioCntmReadStatusEx(short Id, short ChNo, unsigned long *Sts);
AioCntmReadStatusEx = caio_dll.AioCntmReadStatusEx
AioCntmReadStatusEx.restype = ctypes.c_long
AioCntmReadStatusEx.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.c_ulong)]

#----------------------------------------
# Notify function
#----------------------------------------
# C Prototype: long WINAPI AioCntmNotifyCountUp(short Id, short ChNo, short RegNo, unsigned long Count, HANDLE hWnd);
AioCntmNotifyCountUp = caio_dll.AioCntmNotifyCountUp
AioCntmNotifyCountUp.restype = ctypes.c_long
AioCntmNotifyCountUp.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_short, ctypes.c_ulong, ctypes.wintypes.HANDLE]

# C Prototype: long WINAPI AioCntmStopNotifyCountUp(short Id, short ChNo, short RegNo);
AioCntmStopNotifyCountUp = caio_dll.AioCntmStopNotifyCountUp
AioCntmStopNotifyCountUp.restype = ctypes.c_long
AioCntmStopNotifyCountUp.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_short]

# C Prototype: long WINAPI AioCntmCountUpCallbackProc(short Id , void *CallBackProc , void *Param);
AioCntmCountUpCallbackProc = caio_dll.AioCntmCountUpCallbackProc
AioCntmCountUpCallbackProc.restype = ctypes.c_long
AioCntmCountUpCallbackProc.argtypes = [ctypes.c_short, PAIO_MATCH_CALLBACK, ctypes.c_void_p]

# C Prototype: long WINAPI AioCntmNotifyCounterError(short Id, HANDLE hWnd);
AioCntmNotifyCounterError = caio_dll.AioCntmNotifyCounterError
AioCntmNotifyCounterError.restype = ctypes.c_long
AioCntmNotifyCounterError.argtypes = [ctypes.c_short, ctypes.wintypes.HANDLE]

# C Prototype: long WINAPI AioCntmStopNotifyCounterError(short Id);
AioCntmStopNotifyCounterError = caio_dll.AioCntmStopNotifyCounterError
AioCntmStopNotifyCounterError.restype = ctypes.c_long
AioCntmStopNotifyCounterError.argtypes = [ctypes.c_short]

# C Prototype: long WINAPI AioCntmCounterErrorCallbackProc(short Id , void *CallBackProc , void *Param);
AioCntmCounterErrorCallbackProc = caio_dll.AioCntmCounterErrorCallbackProc
AioCntmCounterErrorCallbackProc.restype = ctypes.c_long
AioCntmCounterErrorCallbackProc.argtypes = [ctypes.c_short, PAIO_COUNTER_ERR_CALLBACK, ctypes.c_void_p]

# C Prototype: long WINAPI AioCntmNotifyCarryBorrow(short Id, HANDLE hWnd);
AioCntmNotifyCarryBorrow = caio_dll.AioCntmNotifyCarryBorrow
AioCntmNotifyCarryBorrow.restype = ctypes.c_long
AioCntmNotifyCarryBorrow.argtypes = [ctypes.c_short, ctypes.wintypes.HANDLE]

# C Prototype: long WINAPI AioCntmStopNotifyCarryBorrow(short Id);
AioCntmStopNotifyCarryBorrow = caio_dll.AioCntmStopNotifyCarryBorrow
AioCntmStopNotifyCarryBorrow.restype = ctypes.c_long
AioCntmStopNotifyCarryBorrow.argtypes = [ctypes.c_short]

# C Prototype: long WINAPI AioCntmCarryBorrowCallbackProc(short Id, void *CallBackProc, void *Param);
AioCntmCarryBorrowCallbackProc = caio_dll.AioCntmCarryBorrowCallbackProc
AioCntmCarryBorrowCallbackProc.restype = ctypes.c_long
AioCntmCarryBorrowCallbackProc.argtypes = [ctypes.c_short, PAIO_CARRY_BORROW_CALLBACK, ctypes.c_void_p]

# C Prototype: long WINAPI AioCntmNotifyTimer(short Id, unsigned long TimeValue, HANDLE hWnd);
AioCntmNotifyTimer = caio_dll.AioCntmNotifyTimer
AioCntmNotifyTimer.restype = ctypes.c_long
AioCntmNotifyTimer.argtypes = [ctypes.c_short, ctypes.c_ulong, ctypes.wintypes.HANDLE]

# C Prototype: long WINAPI AioCntmStopNotifyTimer(short Id);
AioCntmStopNotifyTimer = caio_dll.AioCntmStopNotifyTimer
AioCntmStopNotifyTimer.restype = ctypes.c_long
AioCntmStopNotifyTimer.argtypes = [ctypes.c_short]

# C Prototype: long WINAPI AioCntmTimerCallbackProc(short Id , void *CallBackProc , void *Param);
AioCntmTimerCallbackProc = caio_dll.AioCntmTimerCallbackProc
AioCntmTimerCallbackProc.restype = ctypes.c_long
AioCntmTimerCallbackProc.argtypes = [ctypes.c_short, PAIO_TIMEUP_CALLBACK, ctypes.c_void_p]


#----------------------------------------
# General purpose input function
#----------------------------------------
# C Prototype: long WINAPI AioCntmInputDIByte(short Id, short Reserved, BYTE *bData);
AioCntmInputDIByte = caio_dll.AioCntmInputDIByte
AioCntmInputDIByte.restype = ctypes.c_long
AioCntmInputDIByte.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.c_ubyte)]

# C Prototype: long WINAPI AioCntmOutputDOBit(short Id, short AiomChNo, short Reserved, BYTE OutData);
AioCntmOutputDOBit = caio_dll.AioCntmOutputDOBit
AioCntmOutputDOBit.restype = ctypes.c_long
AioCntmOutputDOBit.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_short, ctypes.c_ubyte]
"""

