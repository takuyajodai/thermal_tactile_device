#================================================================
#================================================================
# API-AIO(WDM)
# AiLong Sample
#                                                CONTEC Co., Ltd.
#参考　http://www.s12600.net/psy/python/21-3.html
#
#================================================================
#================================================================
import ctypes
import ctypes.wintypes
import sys
import msvcrt
import caio

import math
import numpy as np
import matplotlib.pyplot as plt
import time

AI_END_EVENT_HAPPENED   = 1
AI_ERR_HAPPENED         = 2
CALLBACK_PROCESS_END    = 8
AiTotalSamplingTimes = ctypes.c_long(0)             # The total number of samplings to be retrieved

#データ収集用
count = 0 #コールバック回数 
data = []

#x = np.array(range(0, count))
#y = np.array(data)
#plt.figure(figsize=(15, 6))
#plt.xlabel("callback count")
#plt.ylabel("temperature")
#plt.plot(x, y, color = "red", marker = ".", label = "temp change")
#plt.legend()
#lines = plt.plot(x,y)

class RealtimePlot1D():
    def __init__(
        self,
        x_tick,
        length,
        xlabel="time",
        ylabel="temperature",
        title="RealtimePlot1D",
        color="r",
        marker="-",
        alpha=1.0,
        ylim=None
    ):
        self.x_tick = x_tick
        self.length = length
        self.color = color
        self.marker = marker
        self.alpha = 1.0
        self.ylim = ylim
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.title = title
        self.line = None

        #プロット初期化
        self.init_plot()

    def init_plot(self):
        self.x_vec = np.arange(0, self.length) * self.x_tick - self.length * self.x_tick
        self.y_vec = np.zeros(self.length)
        
        plt.ion()
        fig = plt.figure(figsize=(10,6))
        ax = fig.add_subplot(111)
        
        self.line = ax.plot(self.x_vec, self.y_vec, 
                            self.marker, color=self.color, 
                            alpha=self.alpha)  
        if self.ylim is not None:
            plt.ylim(self.ylim[0], self.ylim[1])
        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)
        plt.title(self.title)
        plt.grid()
        plt.show()
        
        self.index = 0
        self.x_data = -self.x_tick
        self.pretime = 0.0
        self.fps = 0.0

    def update_index(self):
        self.index = self.index + 1 if self.index < self.length-1 else 0
        
    def update_ylim(self, y_data):
        ylim = self.line[0].axes.get_ylim()
        if   y_data < ylim[0]:
            plt.ylim(y_data*1.1, ylim[1])
        elif y_data > ylim[1]:
            plt.ylim(ylim[0], y_data*1.4)
            
    def compute_fps(self):
        curtime = time.time()
        time_diff = curtime - self.pretime
        self.fps = 1.0 / (time_diff + 1e-16)
        self.pretime = curtime 

    def update(self, y_data):
        # プロットする配列の更新
        self.x_data += self.x_tick
        self.y_vec[self.index] = y_data
        
        y_pos = self.index + 1 if self.index < self.length else 0
        tmp_y_vec = np.r_[self.y_vec[y_pos:self.length], self.y_vec[0:y_pos]]
        self.line[0].set_ydata(tmp_y_vec)
        if self.ylim is None:
            self.update_ylim(y_data)
        
        plt.title(f"fps: {self.fps:0.1f} Hz")
        plt.pause(0.01)
        
        # 次のプロット更新のための処理
        self.update_index()
        self.compute_fps()

#================================================================
# Callback routine
#================================================================
def CallBackProc(dev_id, AiEvent, wparam, lparam, param):
    #----------------------------------------
    # Declare variables
    #----------------------------------------
    err_str = ctypes.create_string_buffer(256)      # Error string
    lret = ctypes.c_long()                          # Return values of functions
    AiChannels = ctypes.c_short()                   # Number of the used channels
    AiStatus = ctypes.c_long()                      # The current status
    AiSamplingCount = ctypes.c_long()               # The current number of samplings
    DATA_MAX = 16000                                # The size of converted data
    AiDataType = ctypes.c_float * DATA_MAX          # Create the array type (Converted data)
    AiData = AiDataType()                           # Converted data

    global count
    global data
    global lines

    c_short_ptr = ctypes.cast(param, ctypes.POINTER(ctypes.c_short))
    #----------------------------------------
    # Event that data of the specified sampling times are stored
    #----------------------------------------
    if AiEvent == caio.AIOM_AIE_DATA_NUM:
        #----------------------------------------
        # Get the number of channels
        #----------------------------------------
        if lret.value != 0:
            caio.AioGetErrorString(lret, err_str)
            print(f"AioGetAiChannels = {lret.value} : {err_str.value.decode('sjis')}")
            c_short_ptr.contents.value |= CALLBACK_PROCESS_END
            return
        #----------------------------------------
        # Get the status
        #----------------------------------------
        lret.value = caio.AioGetAiStatus(dev_id, ctypes.byref(AiStatus))
        if lret.value != 0:
            caio.AioGetErrorString(lret, err_str)
            print(f"AioGetAiStatus = {lret.value} : {err_str.value.decode('sjis')}")
            c_short_ptr.contents.value |= CALLBACK_PROCESS_END
            return
        #----------------------------------------
        # Get the number of sampling data stored in the memory
        #----------------------------------------
        lret.value = caio.AioGetAiSamplingCount(dev_id, ctypes.byref(AiSamplingCount))
        if lret.value != 0:
            caio.AioGetErrorString(lret, err_str)
            print(f"AioGetAiSamplingCount = {lret.value} : {err_str.value.decode('sjis')}")
            c_short_ptr.contents.value |= CALLBACK_PROCESS_END
            return
        #----------------------------------------
        # Get the converted data
        #----------------------------------------
        if AiSamplingCount.value >= 100:
            #----------------------------------------
            # Adjust to prevent the retrieved number of samplings from exceeding the size of array for storing data
            #----------------------------------------
            if AiSamplingCount.value * AiChannels.value > DATA_MAX:
                AiSamplingCount.value = DATA_MAX // AiChannels.value
            #----------------------------------------
            # Get the converted data
            #----------------------------------------
            lret.value = caio.AioGetAiSamplingDataEx(dev_id, ctypes.byref(AiSamplingCount), AiData)
            if lret.value != 0:
                caio.AioGetErrorString(lret, err_str)
                print(f"AioGetAiSamplingDataEx = {lret.value} : {err_str.value.decode('sjis')}")
                c_short_ptr.contents.value |= CALLBACK_PROCESS_END
                return
            AiTotalSamplingTimes.value += AiSamplingCount.value
            #print("電圧" + str(AiData[0]) + "\n")
            #B parameter equation
            Vol = AiData[0]
            current = 0.000487
            b = 3889
            registance = Vol / current
            temp = (b / (math.log(registance) + 3.8334)) - 273.15
            print("\r{:.3f}".format(temp) + "℃", end = '', flush = True)
            data.append(round(temp, 3))
            count += 1
            

            
        #----------------------------------------
        # Display the number of samplings and the status
        #----------------------------------------
        #print(f"\rThe total number of samplings : {AiTotalSamplingTimes.value:6d} Samplings times : {AiSamplingCount.value:5d} Status : {AiStatus.value:2x}H", end='', flush=True)
    #----------------------------------------
    # Overflow Event
    #----------------------------------------
    elif AiEvent == caio.AIOM_AIE_OFERR:
        c_short_ptr.contents.value |= AI_ERR_HAPPENED
        print(f"\rConverting stopped because of overflow", end='', flush=True)
    #----------------------------------------
    # Sampling Clock Error Event
    #----------------------------------------
    elif AiEvent == caio.AIOM_AIE_SCERR:
        c_short_ptr.contents.value |= AI_ERR_HAPPENED
        print(f"\rConverting stopped because of sampling clock error", end='', flush=True)
    #----------------------------------------
    # AD Converting Error Event
    #----------------------------------------
    elif AiEvent == caio.AIOM_AIE_ADERR:
        c_short_ptr.contents.value |= AI_ERR_HAPPENED
        print(f"\rConverting stopped because of AD converting error", end='', flush=True)
    #----------------------------------------
    # Device Operation End Event
    #----------------------------------------
    c_short_ptr.contents.value |= CALLBACK_PROCESS_END
    return


pai_callback = caio.PAIO_AI_CALLBACK(CallBackProc)


#================================================================
# Function that checks if a string can be converted to a number
#================================================================
def isnum(str, base):
    try:
        if 10 == base:
            int(str, 10)
        else:
            float(str)
    except:
        return False
    return True


#================================================================
# Main function
#================================================================
def main():
    #----------------------------------------
    # Declare variables
    #----------------------------------------
    err_str = ctypes.create_string_buffer(256)      # Error string
    lret = ctypes.c_long()                          # Return values of functions
    aio_id = ctypes.c_short()                       # ID
    device_name = ctypes.create_string_buffer(50)   # Device name
    AiStatus = ctypes.c_long()                      # The current status
    AiData = ctypes.c_float()                       # Converted data
    CallBackFlag = ctypes.c_short(0)                # Flag of waiting for the callback routine end
    AiSamplingTimes = ctypes.c_long()

    #----------------------------------------
    # Confirm to input the device name
    #----------------------------------------
    device_name = input("Please input device name : ")
    #----------------------------------------
    # Initialize the device
    #----------------------------------------
    #----------------------------------------
    # Initialization
    #----------------------------------------
    lret.value = caio.AioInit(device_name.encode(), ctypes.byref(aio_id))
    if lret.value != 0:
        caio.AioGetErrorString(lret, err_str)
        print(f"AioInit = {lret.value} : {err_str.value.decode('sjis')}")
        sys.exit()
    #----------------------------------------
    # Reset device
    #----------------------------------------
    lret.value = caio.AioResetDevice(aio_id)
    if lret.value != 0:
        caio.AioGetErrorString(lret, err_str)
        print(f"AioResetDevice = {lret.value} : {err_str.value.decode('sjis')}")
        caio.AioExit(aio_id)
        sys.exit()
    #----------------------------------------
    # Set analog input range
    #----------------------------------------
    while True:
        print("\nPlease select analog input range from the following list")
        print("+/-10V\t\t : 0\t0~10V\t\t : 50")
        print("+/-5V\t\t : 1\t0~5V\t\t : 51")
        print("+/-2.5V\t\t : 2\t0~4.095V\t : 52")
        print("+/-1.25V\t : 3\t0~2.5V\t\t : 53")
        print("+/-1V\t\t : 4\t0~1.25V\t\t : 54")
        print("+/-0.625V\t : 5\t0~1V\t\t : 55")
        print("+/-0.5V\t\t : 6\t0~0.5V\t\t : 56")
        print("+/-0.3125V\t : 7\t0~0.25V\t\t : 57")
        print("+/-0.25V\t : 8\t0~0.1V\t\t : 58")
        print("+/-0.125V\t : 9\t0~0.05V\t\t : 59")
        print("+/-0.1V\t\t : 10\t0~0.025V\t : 60")
        print("+/-0.05V\t : 11\t0~0.0125V\t : 61")
        print("+/-0.025V\t : 12\t0~0.01V\t\t : 62")
        print("+/-0.0125V\t : 13\t0~20mA\t\t : 100")
        print("+/-0.01V\t : 14\t4~20mA\t\t : 101")
        print("+/-20mA\t\t : 102\t1~5V\t\t : 150")
        buf = input()
        if False == isnum(buf, 10):
            continue
        AiRange = int(buf)
        break
    print("")
    #----------------------------------------
    # Set the input range
    #----------------------------------------
    lret.value = caio.AioSetAiRangeAll(aio_id, AiRange)
    if lret.value != 0:
        caio.AioGetErrorString(lret, err_str)
        print(f"AioSetAiRangeAll = {lret.value} : {err_str.value.decode('sjis')}")
        caio.AioExit(aio_id)
        sys.exit()
    #----------------------------------------
    # Set the converting conditions
    #----------------------------------------
    #----------------------------------------
    # Set the number of channels : 1 channel
    #----------------------------------------
    AiChannels = 1
    lret.value = caio.AioSetAiChannels(aio_id, AiChannels)
    if lret.value != 0:
        caio.AioGetErrorString(lret, err_str)
        print(f"AioSetAiChannels = {lret.value} : {err_str.value.decode('sjis')}")
        caio.AioExit(aio_id)
        sys.exit()
    #----------------------------------------
    # Set the memory type : FIFO
    #----------------------------------------
    lret.value = caio.AioSetAiMemoryType(aio_id, 0)
    if lret.value != 0:
        caio.AioGetErrorString(lret, err_str)
        print(f"AioSetAiMemoryType = {lret.value} : {err_str.value.decode('sjis')}")
        caio.AioExit(aio_id)
        sys.exit()
    #----------------------------------------
    # Set the clock type : Internal
    #----------------------------------------
    lret.value = caio.AioSetAiClockType(aio_id, 0)
    if lret.value != 0:
        caio.AioGetErrorString(lret, err_str)
        print(f"AioSetAiClockType = {lret.value} : {err_str.value.decode('sjis')}")
        caio.AioExit(aio_id)
        sys.exit()
    #----------------------------------------
    # Set the sampling clock : 1000 usec
    #----------------------------------------
    lret.value = caio.AioSetAiSamplingClock(aio_id, 1000)
    if lret.value != 0:
        caio.AioGetErrorString(lret, err_str)
        print(f"AioSetAiSamplingClock = {lret.value} : {err_str.value.decode('sjis')}")
        caio.AioExit(aio_id)
        sys.exit()
    #----------------------------------------
    # Set the start condition : Software
    #----------------------------------------
    lret.value = caio.AioSetAiStartTrigger(aio_id, 0)
    if lret.value != 0:
        caio.AioGetErrorString(lret, err_str)
        print(f"AioSetAiStartTrigger = {lret.value} : {err_str.value.decode('sjis')}")
        caio.AioExit(aio_id)
        sys.exit()
    #----------------------------------------
    # Set the stop condition : Command
    #----------------------------------------
    lret.value = caio.AioSetAiStopTrigger(aio_id, 4)
    if lret.value != 0:
        caio.AioGetErrorString(lret, err_str)
        print(f"AioSetAiStopTrigger = {lret.value} : {err_str.value.decode('sjis')}")
        caio.AioExit(aio_id)
        sys.exit()
    #----------------------------------------
    # Set the event factor : Device operation end, store the data of the specified sampling times, 
    #                        Overflow, Clock error, AD converting error
    #----------------------------------------
    #コールバック呼び出し条件　デバイス動作終了、指定回数データ格納、サンプリングクロックエラー、オーバーフロー
    AiEvent = caio.AIE_END | caio.AIE_DATA_NUM | caio.AIE_OFERR | caio.AIE_SCERR | caio.AIE_ADERR
    #コールバック関数の呼びだし　これがハンドラ
    lret.value = caio.AioSetAiCallBackProc(aio_id, pai_callback, AiEvent, ctypes.byref(CallBackFlag))
    if lret.value != 0:
        caio.AioGetErrorString(lret, err_str)
        print(f"AioSetAiCallBackProc = {lret.value} : {err_str.value.decode('sjis')}")
        caio.AioExit(aio_id)
        sys.exit()
    #----------------------------------------
    # Set the number of samplings of the event that data of the specified sampling times are stored : 1000
    #----------------------------------------
    #この値データ格納された時にコールバックイベント発生
    lret.value = caio.AioSetAiEventSamplingTimes(aio_id, 100)
    if lret.value != 0:
        caio.AioGetErrorString(lret, err_str)
        print(f"AioSetAiEventSamplingTimes = {lret.value} : {err_str.value.decode('sjis')}")
        caio.AioExit(aio_id)
        sys.exit()
    #----------------------------------------
    # Start Converting
    #----------------------------------------
    #----------------------------------------
    # Reset memory
    #----------------------------------------
    lret.value = caio.AioResetAiMemory(aio_id)
    if lret.value != 0:
        caio.AioGetErrorString(lret, err_str)
        print(f"AioResetAiMemory = {lret.value} : {err_str.value.decode('sjis')}")
        caio.AioExit(aio_id)
        sys.exit()
    #----------------------------------------
    # Start Converting
    #----------------------------------------
    CallBackFlag.value |= CALLBACK_PROCESS_END
    lret.value = caio.AioStartAi(aio_id)
    if lret.value != 0:
        caio.AioGetErrorString(lret, err_str)
        print(f"AioStartAi = {lret.value} : {err_str.value.decode('sjis')}")
        caio.AioExit(aio_id)
        sys.exit()
    print("Start converting, click any key to stop the converting\n")
    #print("Channel\t\tVoltage")

    x_tick = 0.1
    length = 100
    realtime_plot1d = RealtimePlot1D(x_tick, length)
    
    #----------------------------------------
    # Get status of converting
    #----------------------------------------
    while True:
        if count >= 1:
            #x = np.array(range(0, count))
            #y_data = math.log(count)
            y_data = np.array(data[count-1])
            realtime_plot1d.update(y_data)

            #print(count)
            #print(data)
        #----------------------------------------
        # Check AI Error
        #----------------------------------------
        if CallBackFlag.value & AI_ERR_HAPPENED == AI_ERR_HAPPENED or \
           msvcrt.kbhit() != 0:
            break

    

    
    #----------------------------------------
    # Stop Converting
    #----------------------------------------
    print("\n\nStop Converting\n")
    lret.value = caio.AioStopAi(aio_id)
    if lret.value != 0:
        caio.AioGetErrorString(lret, err_str)
        print(f"AioStopAi = {lret.value} : {err_str.value.decode('sjis')}")
        caio.AioExit(aio_id)
        sys.exit()

    
    

    #----------------------------------------
    # Waiting until the callback routine has finished performing
    #----------------------------------------
    while CallBackFlag.value & CALLBACK_PROCESS_END != CALLBACK_PROCESS_END:
        pass
    #----------------------------------------
    # Exit the device
    #----------------------------------------
    lret.value = caio.AioExit(aio_id)
    if lret.value != 0:
        caio.AioGetErrorString(lret, err_str)
        print(f"AioExit = {lret.value} : {err_str.value.decode('sjis')}")
        sys.exit()
    sys.exit()


#----------------------------------------
# Call main function
#----------------------------------------
if __name__ == "__main__":
    
    main()
