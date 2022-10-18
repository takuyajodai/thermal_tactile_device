#================================================================
#================================================================
# API-AIO(WDM)
# AiLong Sample
#                                                CONTEC Co., Ltd.
#参考　http://www.s12600.net/psy/python/21-3.html
#https://org-technology.com/posts/matplotlib-realtime-plot.html

#
#================================================================
#================================================================
import ctypes
import ctypes.wintypes
from email.mime import base
from socket import inet_ntoa
from sqlite3 import SQLITE_CREATE_TEMP_INDEX
import sys
import msvcrt
import caio

import math
import numpy as np
import matplotlib.pyplot as plt
import time
import csv
import random

import plot



AI_END_EVENT_HAPPENED   = 1
AI_ERR_HAPPENED         = 2
CALLBACK_PROCESS_END    = 8
AiTotalSamplingTimes = ctypes.c_long(0)             # The total number of samplings to be retrieved



#データ収集用
count = 0 #コールバック回数 
temp_data = []
initial_time = 0
time_data = []

DATA_MAX = 16000
AoDataType = ctypes.c_float * DATA_MAX          # Create the array type (Converted data)
AoData = AoDataType()
# Vo2.5v初期化用
AoData[0] = float(2.5)

#PID制御用
temp_err_sum = 0
set_temp = 30
soa = 0

toj_flag = False
WAITTIME = 1
ANSTIME = 3

state = 1


length = 100
realtime_plot1d = plot.RealtimePlot1D(length)
x_data = np.zeros(length)

run_once = 0
start = 0




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
    AoChannel = 0                                   # 使用する出力チャンネル

    global count                                    # callback回数カウント
    global initial_time                             # 計測開始時間
    global time_data                                # ラップ時間格納
    global temp_data                                # 温度データ格納

    global AoData

    ki = -0.0003                                    # PID制御パラメータ
    kp = -0.5                                       # PID制御パラメータ
    global temp_err_sum                             # PID制御パラメータ
    global set_temp                                 # 目標温度
    global toj_flag
    global soa

    c_short_ptr = ctypes.cast(param, ctypes.POINTER(ctypes.c_short))

    def cal_temp(volt):
        #B parameter equation
        current = 0.000487
        b = 3889
        registance = volt / current
        current_temp = (b / (math.log(registance) + 3.8334)) - 273.15

        return current_temp

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
            Vol1 = AiData[0]
            Vol2 = AiData[1]
            Vol3 = AiData[2]
            current_temp = cal_temp(Vol1)
            temp2 = cal_temp(Vol2)
            temp3 = cal_temp(Vol3)
            
            #経過時間
            tmp_time = time.perf_counter()
            current_time = tmp_time - initial_time

            #ログ出力
            #print("\r{:.3f}".format(temp) + "℃　" + "{:.3f}".format(current_time) + "sec", end = '', flush = True)
            
            #アナログ簡易出力
            #a = random.randint(0,5)
            #TOJ動作状態かつ、刺激提示状態であるとき
            if toj_flag == True and (state == 2 or state == 3):
                #PIDコントロール
                set_temp = 39
                temp_err = float(set_temp) - current_temp
                temp_err_sum += temp_err
                #print(temp_err_sum)
                Vo = (kp * temp_err) + (ki * temp_err_sum) + 2.5
                AoData[count] = Vo
                lret = caio.AioSingleAoEx(dev_id, AoChannel, AoData[count])
                if lret != 0:
                    caio.AioGetErrorString(lret, err_str)
                    print(f"AioSingleAoEx = {lret.value}:{err_str.value.decode('sjis')}")
            else:
                Vo = 2.5
                AoData[count] = Vo
                lret = caio.AioSingleAoEx(dev_id, AoChannel, AoData[count])
                if lret != 0:
                    caio.AioGetErrorString(lret, err_str)
                    print(f"AioSingleAoEx = {lret.value}:{err_str.value.decode('sjis')}")

            #セーフティ
            if current_temp <=15 or current_temp >= 45:
                toj_flag = False

            #ログ出力
            print("\r{:.3f}".format(current_temp) + "℃  " + "{:.3f}".format(temp2) + "℃  " + "{:.3f}".format(temp3) + "℃  " + "{:.3f}".format(AoData[count]) + "V " + "{:.3f}".format(current_time) + "sec", end = '', flush = True)
            
            #配列格納
            time_data.append(round(current_time, 3))
            temp_data.append(round(current_temp, 3))
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

    
def graph():
    global x_data
    global realtime_plot1d

    if count >= 1:
        x_data = np.append(x_data, float(time_data[count-1]))
        x_data = np.delete(x_data, 0)
        y_data = np.array(temp_data[count-1])
        realtime_plot1d.update(x_data, y_data)


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

    global set_temp
    global soa
    global toj_flag
    global state
    global run_once
    global start

    #----------------------------------------
    # Confirm to input the device name
    #----------------------------------------
    #device_name = input("Please input device name : ")
    device_name = "AIO000"
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
    """
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
    """
    #----------------------------------------
    # Set aimed temparture
    #----------------------------------------
    while True:
        print("\nPlease input the SOA: ", end='')
        buf = input()
        #if False == isnum(buf, 10):
            #continue
        soa = buf
        break
    print("")
    #----------------------------------------
    # Set the input range
    #----------------------------------------
    AiRange = int(0)
    lret.value = caio.AioSetAiRangeAll(aio_id, AiRange)
    if lret.value != 0:
        caio.AioGetErrorString(lret, err_str)
        print(f"AioSetAiRangeAll = {lret.value} : {err_str.value.decode('sjis')}")
        caio.AioExit(aio_id)
        sys.exit()
    #----------------------------------------
    # Set the output range (0~5v固定)
    #----------------------------------------
    AoRange = int(0)
    lret.value = caio.AioSetAoRangeAll(aio_id, AoRange)
    if lret.value != 0:
        caio.AioGetErrorString(lret, err_str)
        print(f"AioSetAoRangeAll = {lret.value} : {err_str.value.decode('sjis')}")
        caio.AioExit(aio_id)
        sys.exit()
    #----------------------------------------
    # Set the converting conditions
    #----------------------------------------
    #----------------------------------------
    # Set the number of channels : 3 channel
    #----------------------------------------
    AiChannels = 3
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
    lret.value = caio.AioSetAiSamplingClock(aio_id, 200)
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
    
    lret.value = caio.AioResetAoMemory(aio_id)
    if lret.value != 0:
        caio.AioGetErrorString(lret, err_str)
        print(f"AioResetAoMemory = {lret.value} : {err_str.value.decode('sjis')}")
        caio.AioExit(aio_id)
        sys.exit()

    # offvoltageの初期値
    #AoData[0] = float(2.5)
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


    #----------------------------------------
    # Get status of converting
    #----------------------------------------
    while True:
        #----------------------------------------
        # Check AI Error
        #----------------------------------------
        if CallBackFlag.value & AI_ERR_HAPPENED == AI_ERR_HAPPENED:
            break

        #プログラムの停止・TOJの開始　h:halt s:start
        if msvcrt.kbhit() != 0:
            if msvcrt.getch().decode() == 's':
                toj_flag = True
            else:
                break
        
        if toj_flag == True:
            
            if run_once == 0:
                start = time.perf_counter()
                run_once = 1
            if state == 1:
                end = time.perf_counter()
                if (end - start >= 3):
                    print("waitいけたで")
                    state = 2
                    run_once = 0
            elif state == 2:
                end = time.perf_counter()
                if (end - start >= float(soa)):
                    print("doいけたで")
                    lret.value = caio.AioOutputDoBit ( aio_id , 0 , 1 )
                    time.sleep(0.01)
                    lret.value = caio.AioOutputDoBit ( aio_id , 0 , 0 )
                    state = 3
                    run_once = 0
            elif state == 3:
                print("提示後いけたで")
                if(temp_data[count-1] >= 39):
                    state = 4
                    run_once = 0
            elif state == 4:
                end = time.perf_counter()
                if (end - start >= 5):
                    print("ansいけたで")
                    state = 1
                    run_once = 0

        graph()

            
        
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

    #ファイル出力
    f = open('./result.csv', 'w') 
    header = ["time(sec)", "temp(℃)"]
    writer = csv.writer(f)
    writer.writerow(header)
    result = zip(time_data, temp_data)
    writer.writerows(result)
    f.close()
    

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
