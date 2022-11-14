#================================================================
#================================================================
# API-AIO(WDM)
# TOJ task for thermal and tactile cue
#                                                
# 参考　http://www.s12600.net/psy/python/21-3.html
# https://org-technology.com/posts/matplotlib-realtime-plot.html
# device : AIO-160802AY-USB
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

AI_ERR_HAPPENED     = 2


#================================================================
# Main function
#================================================================
def main():
    #----------------------------------------
    # Declare variables
    #----------------------------------------
    ret = ctypes.c_long()                           # Return values of functions
    aio_id = ctypes.c_short()                       # device id
    err_str = ctypes.create_string_buffer(256)      # Error string
    AiSamplingTimes = ctypes.c_long()
    DATA_MAX = 16000                                # The size of converted data
    AiDataType = ctypes.c_float * DATA_MAX          # Create the array type (Converted data)
    AiData = AiDataType()                           # Converted data
    AiSamplingCount = ctypes.c_long()               # The current number of samplings
    AiChannels = ctypes.c_short()                   # Number of the used channels
    AiTotalSamplingTimes = ctypes.c_long(0)         # The total number of samplings to be retrieved
    AoChannel = 0                                   # 使用する出力チャンネル

    exp_flag = False                                # セッション中か
    state = 1                                       # 
    temp = []                                       # temp[0] : device temp, temp[1] : skin temp change, temp[2] : skin_temp
    run_once = 0
    run_once_solenoid = 0
    trial_count = 0                                 # 一試行ごとにインクリメント
    state_text = ""

    # parameter
    ki = -0.0003
    kp = -0.5

    # temp cal
    current = 0.000487
    b = 3889

    # PI control
    temp_err_sum = 0

    #----------------------------------------
    # Declare function
    #----------------------------------------

    # 関数呼び出しのオーバヘッドをできるだけ削減するためにベタ打ち
    """
    def cal_temp(volt):
        #B parameter equation
        current = 0.000487
        b = 3889
        registance = volt / current
        current_temp = (b / (math.log(registance) + 3.8334)) - 273.15

        return current_temp

    """
    def pi_contorl(aimed_temp, current_temp, temp_err_sum):
        # PIコントロール
        temp_err = float(aimed_temp) - current_temp
        temp_err_sum += temp_err
        
        Vo = (kp * temp_err) + (ki * temp_err_sum) + 2.5
        ret.value = caio.AioSingleAoEx(aio_id, AoChannel, Vo)
        if ret.value != 0:
            caio.AioGetErrorString(ret.value, err_str)
            print(f"AioSingleAoEx = {ret.value}:{err_str.value.decode('sjis')}")
        return Vo
    #----------------------------------------
    # Initialization
    #----------------------------------------
    device_name = "AIO000"
    ret.value = caio.AioInit(device_name.encode(), ctypes.byref(aio_id))
    if ret.value != 0:
        caio.AioGetErrorString(ret, err_str)
        print(f"AioInit = {ret.value} : {err_str.value.decode('sjis')}")
        sys.exit()

    #----------------------------------------
    # Reset device
    #----------------------------------------
    ret.value = caio.AioResetDevice(aio_id)
    if ret.value != 0:
        caio.AioGetErrorString(ret, err_str)
        print(f"AioResetDevice = {ret.value} : {err_str.value.decode('sjis')}")
        caio.AioExit(aio_id)
        sys.exit()

    #----------------------------------------
    # Step1 Input Method 
    # AIO-160802AY-USBはシングルエンド入力のみ
    #----------------------------------------

    #----------------------------------------
    # Step2 Channel Sequence
    # 変換順序はそのまま
    #----------------------------------------

    #----------------------------------------
    # Step3 Set the number of channels : 3 channels
    #----------------------------------------
    aiChannels = 3
    ret.value = caio.AioSetAiChannels(aio_id, aiChannels)
    if ret.value != 0:
        caio.AioGetErrorString(ret, err_str)
        print(f"AioSetAiChannels = {ret.value} : {err_str.value.decode('sjis')}")
        caio.AioExit(aio_id)
        sys.exit()

    # get the number of channels
    ret = ctypes.c_long()
    ret.value = caio.AioGetAiChannels (aio_id , ctypes.byref(AiChannels) )
    temp = list(range(AiChannels.value))

    #----------------------------------------
    # Step4 Set the analog input range
    #----------------------------------------
    # ±10v
    aiRange = int(0)
    ret.value = caio.AioSetAiRangeAll(aio_id, aiRange)
    if ret.value != 0:
        caio.AioGetErrorString(ret, err_str)
        print(f"AioSetAiRangeAll = {ret.value} : {err_str.value.decode('sjis')}")
        caio.AioExit(aio_id)
        sys.exit()

    #----------------------------------------
    # Set the analog output range (0~5v固定)
    #----------------------------------------
    aoRange = int(0)
    ret.value = caio.AioSetAoRangeAll(aio_id, aoRange)
    if ret.value != 0:
        caio.AioGetErrorString(ret, err_str)
        print(f"AioSetAoRangeAll = {ret.value} : {err_str.value.decode('sjis')}")
        caio.AioExit(aio_id)
        sys.exit()


    #----------------------------------------
    # Step5 Set the transfer type
    # デバイスバッファモードを使用（デフォルト）
    #----------------------------------------
    
    #----------------------------------------
    # Step6 Set the memory type : FIFO
    #----------------------------------------
    ret.value = caio.AioSetAiMemoryType(aio_id, 0)
    if ret.value != 0:
        caio.AioGetErrorString(ret, err_str)
        print(f"AioSetAiMemoryType = {ret.value} : {err_str.value.decode('sjis')}")
        caio.AioExit(aio_id)
        sys.exit()

    #----------------------------------------
    # Step7 Set the clock type : Internal
    #----------------------------------------
    ret.value = caio.AioSetAiClockType(aio_id, 0)
    if ret.value != 0:
        caio.AioGetErrorString(ret, err_str)
        print(f"AioSetAiClockType = {ret.value} : {err_str.value.decode('sjis')}")
        caio.AioExit(aio_id)
        sys.exit()

    #----------------------------------------
    # Step8 Set the start condition : Software
    #----------------------------------------
    ret.value = caio.AioSetAiStartTrigger(aio_id, 0)
    if ret.value != 0:
        caio.AioGetErrorString(ret, err_str)
        print(f"AioSetAiStartTrigger = {ret.value} : {err_str.value.decode('sjis')}")
        caio.AioExit(aio_id)
        sys.exit()
    #----------------------------------------
    # Step9 Set the stop condition : Command
    #----------------------------------------
    ret.value = caio.AioSetAiStopTrigger(aio_id, 4)
    if ret.value != 0:
        caio.AioGetErrorString(ret, err_str)
        print(f"AioSetAiStopTrigger = {ret.value} : {err_str.value.decode('sjis')}")
        caio.AioExit(aio_id)
        sys.exit()

    #----------------------------------------
    # Step10 Set the sampling delay
    # なし
    #----------------------------------------

    #----------------------------------------
    # Step11 Set the repeat times
    # なし
    #----------------------------------------

    #----------------------------------------
    # Step12 Set the event
    # callbackfuncなし
    #----------------------------------------

    #----------------------------------------
    # Set the sampling clock : 1000 usec
    #----------------------------------------
    ret.value = caio.AioSetAiSamplingClock(aio_id, 1000)
    if ret.value != 0:
        caio.AioGetErrorString(ret, err_str)
        print(f"AioSetAiSamplingClock = {ret.value} : {err_str.value.decode('sjis')}")
        caio.AioExit(aio_id)
        sys.exit()

    #----------------------------------------
    # Reset memory
    #----------------------------------------
    ret.value = caio.AioResetAiMemory(aio_id)
    if ret.value != 0:
        caio.AioGetErrorString(ret, err_str)
        print(f"AioResetAiMemory = {ret.value} : {err_str.value.decode('sjis')}")
        caio.AioExit(aio_id)
        sys.exit()

    #----------------------------------------
    # SOAファイルよみこみ (csv)
    #----------------------------------------
    with open('./soa_input.csv') as f:
        reader = csv.reader(f)
        soa_list = [row for row in reader]
        print(soa_list)
        


    #----------------------------------------
    # Start Converting
    #----------------------------------------
    ret.value = caio.AioStartAi(aio_id)
    if ret.value != 0:
        caio.AioGetErrorString(ret, err_str)
        print(f"AioStartAi = {ret.value} : {err_str.value.decode('sjis')}")

        caio.AioExit(aio_id)
        sys.exit()
    print("Start converting, click any key to stop the converting\n")


    #----------------------------------------
    # Get status of converting
    #----------------------------------------
    while trial_count < len(soa_list):
        #----------------------------------------
        # Get the number of sampling data stored in the memory
        #----------------------------------------
        ret.value = caio.AioGetAiSamplingCount(aio_id, ctypes.byref(AiSamplingCount))
        if ret.value != 0:
            caio.AioGetErrorString(ret, err_str)
            print(f"AioGetAiSamplingCount = {ret.value} : {err_str.value.decode('sjis')}")
            return
        #print(AiSamplingCount.value)

        if AiSamplingCount.value >= 10:
            #----------------------------------------
            # Adjust to prevent the retrieved number of samplings from exceeding the size of array for storing data
            #----------------------------------------
            if AiSamplingCount.value * AiChannels.value > DATA_MAX:
                AiSamplingCount.value = DATA_MAX // AiChannels.value
                print("たぶんこれ絶対出力されない")

            #AiSamplingTimes.value = 1000
            ret.value = caio.AioGetAiSamplingDataEx (aio_id , ctypes.byref(AiSamplingCount) , AiData)
            if ret.value != 0:
                caio.AioGetErrorString(ret, err_str)
                print(f"AioGetAiSamplingDataEx = {ret.value} : {err_str.value.decode('sjis')}")
                return
            AiTotalSamplingTimes.value += AiSamplingCount.value

        #----------------------------------------
        # Check AI Error
        #----------------------------------------
        #if AI_ERR_HAPPENED == AI_ERR_HAPPENED:
        #    break

        #プログラムの停止・TOJの開始　s:start
        if msvcrt.kbhit() != 0:
            if msvcrt.getch().decode() == 's':
                exp_flag = True
            else:
                break

        if exp_flag == True:
            #データ収集　(共通)
            # temp[0] : device temp, temp[1] : skin temp change, temp[2] : skin_temp
            for i in range(AiChannels.value):
                volt = AiData[i]
                registance = volt / current
                current_temp = (b / (math.log(registance) + 3.8334)) - 273.15
                #temp[i] = cal_temp(AiData[i])
                temp[i] = current_temp

            if run_once == 0:
                start = AiTotalSamplingTimes.value
                start_time = time.perf_counter()
                run_once = 1

            # キャリブレーション
            if state == 1:
                state_text = "WAITフェーズ"
                end = AiTotalSamplingTimes.value
                end_time = time.perf_counter()
                if (end - start >= 4000): 
                    print(end_time - start_time)
                    state = 2
                    run_once = 0
                    temp_err_sum = 0
                Vo = pi_contorl(temp[2], temp[0], temp_err_sum)
            
            # 提示　先行のもの    
            elif state == 2:
                end = AiTotalSamplingTimes.value
                end_time = time.perf_counter()

                soa = int(soa_list[trial_count][1])
                # SOAが正の場合 触覚先行
                if soa >= 0:
                    ret.value = caio.AioOutputDoBit ( aio_id , 0 , 1 )
                    time.sleep(0.01)
                    ret.value = caio.AioOutputDoBit ( aio_id , 0 , 0 )
                    
                    state_text = "BEFORE DOフェーズ 触覚"
                    print(end_time - start_time)
                    state = 3
                    run_once = 0
                    temp_err_sum = 0
                # SOAが負の場合 熱先行
                else:
                    state_text = "BEFORE DOフェーズ 熱"
                    Vo = pi_contorl(temp[2] - 7, temp[0], temp_err_sum)
                    if (end - start >= abs(soa)):
                        print(end_time - start_time)
                        state = 3
                        run_once = 0
                        temp_err_sum = 0

            elif state == 3:
                end = AiTotalSamplingTimes.value
                end_time = time.perf_counter()

                soa = int(soa_list[trial_count][1])

                # SOAが正の場合 触覚先行
                if soa >= 0:
                    state_text = "LATER DOフェーズ 熱"
                    if (end - start >= abs(soa)):
                        Vo = pi_contorl(temp[2] - 7, temp[0], temp_err_sum)
                        if (end - start >= 3000 - abs(soa)):
                            print(end_time - start_time)
                            state = 4
                            run_once = 0
                            temp_err_sum = 0           
                # SOAが負の場合 熱先行
                else:
                    state_text = "LATER DOフェーズ 触覚"
                    if run_once_solenoid == 0:
                        ret.value = caio.AioOutputDoBit ( aio_id , 0 , 1 )
                        time.sleep(0.01)
                        ret.value = caio.AioOutputDoBit ( aio_id , 0 , 0 )
                        run_once_solenoid = 1
                    Vo = pi_contorl(temp[2] - 7, temp[0], temp_err_sum)
                    if (end - start >= 3000 - abs(soa)):
                        print(end_time - start_time)
                        state = 4
                        run_once = 0
                        run_once_solenoid = 0
                        temp_err_sum = 0
                    
                    

            elif state == 4:
                state_text = "ANSフェーズ"
                end = AiTotalSamplingTimes.value
                end_time = time.perf_counter()
                if (end - start >= 3000):
                    print(end_time - start_time)
                    state = 1
                    run_once = 0
                    temp_err_sum = 0
                    trial_count += 1

                Vo = pi_contorl(temp[2], temp[0], temp_err_sum)
                

            # セーフティ
            if temp[0] <= 15 or temp[0] >= 45:
                exp_flag = False

            print("\rデバイス温 {:.3f}".format(temp[0]) + "℃  " +\
                "皮膚温変化 {:.3f}".format(temp[1]) + "℃  " +\
                "皮膚温 {:.3f}".format(temp[2]) + "℃  " +\
                #"{:.0f}".format(AiSamplingCount.value) + "回  " +\
                "サンプリング回数{:.0f}".format(AiTotalSamplingTimes.value) + "回  " +\
                "{:.3f}".format(Vo) + "V  " +\
                "トライアル{:.0f}".format(trial_count) + "回  " +\
                state_text, end = ' ', flush = True)

        else:
            Vo = 2.5
            ret.value = caio.AioSingleAoEx(aio_id, AoChannel, Vo)
            if ret.value != 0:
                caio.AioGetErrorString(ret.value, err_str)
                print(f"AioSingleAoEx = {ret.value}:{err_str.value.decode('sjis')}")


    #----------------------------------------     
    # Stop Converting
    #----------------------------------------
    print("\n\nStop Converting\n")
    Vo = 2.5
    ret.value = caio.AioSingleAoEx(aio_id, AoChannel, Vo)
    if ret.value != 0:
        caio.AioGetErrorString(ret.value, err_str)
        print(f"AioSingleAoEx = {ret.value}:{err_str.value.decode('sjis')}")
    ret.value = caio.AioStopAi(aio_id)
    if ret.value != 0:
        caio.AioGetErrorString(ret, err_str)
        print(f"AioStopAi = {ret.value} : {err_str.value.decode('sjis')}")
        caio.AioExit(aio_id)
        sys.exit()

    #ファイル出力
    """
    f = open('./result.csv', 'w') 
    header = ["time(sec)", "temp(℃)"]
    writer = csv.writer(f)
    writer.writerow(header)
    result = zip(time_data, temp_data)
    writer.writerows(result)
    f.close()
    """

    #----------------------------------------
    # Exit the device
    #----------------------------------------
    ret.value = caio.AioExit(aio_id)
    if ret.value != 0:
        caio.AioGetErrorString(ret, err_str)
        print(f"AioExit = {ret.value} : {err_str.value.decode('sjis')}")
        sys.exit()
    sys.exit()


#----------------------------------------
# Call main function
#----------------------------------------
if __name__ == "__main__":
    
    main()