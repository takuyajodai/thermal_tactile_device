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
from playsound import playsound
import winsound
from ctypes import windll
from SOA_generator import generate_soa_list

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
    DATA_MAX = 16000                                # The size of converted data
    AiDataType = ctypes.c_float * DATA_MAX          # Create the array type (Converted data)
    AiData = AiDataType()                           # Converted data
    AiChannels = ctypes.c_short()                   # Number of the used channels
    AoChannel = 0                                   # 使用する出力チャンネル


    temp = []                                       # temp[0] : device temp, temp[1] : skin temp change, temp[2] : skin_temp
    exp_flag = False                                # セッション中か
    state = 1
    run_once = 0
    run_once_sound = 0
    run_once_solenoid = 0
    trial_count = 0                                 # 一試行ごとにインクリメント
    state_text = ""
    total_time = 0
    compare_temp = 33                               # Waitの最初に皮膚温の代表値として-7℃のために取得


    csv_data = [[]]
    ans_data = [[]]
    index = 0

    remaining_time = 3


    # temp cal
    current = 0.000487
    b = 3889

    # parameter
    ki = -0.0003
    kp = -0.5

    # PI control
    temp_err_sum = 0


    #----------------------------------------
    # Declare function
    #----------------------------------------
    def pi_control(aimed_temp, current_temp, temp_err_sum):
        # PIコントロール

        temp_err = float(aimed_temp) - current_temp
        temp_err_sum += temp_err

        
        Vo = (kp * temp_err) + (ki * temp_err_sum) + 2.5
        
        start = time.perf_counter()
        ret.value = caio.AioSingleAoEx(aio_id, AoChannel, Vo)
        end = time.perf_counter()
        #print('AioSingleAoEx time = {:.5f} Seconds'.format(end - start))
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
    """
    with open('./soa_input.csv') as f:
        reader = csv.reader(f)
        soa_list = [row for row in reader]
        print(soa_list)
    """

    soa_list = generate_soa_list()
    practice_list = [-1000, 1000, -1000, 1000, -1000, 1000, -1000, 1000]
    #soa_list = [[i, practice_list[i]] for i in range(len(practice_list))]
    print(soa_list)

    # 遅延を考慮　すべて-117msする
    subtractor = 117
    for i in range(len(soa_list)):
        soa_list[i][1] -= subtractor
    #print(soa_list)

    print("Put the subject name here\n")
    subject_name = input()

    print("Start converting, click any key to stop the converting\n")

    # winidowsのOSタイマーの精度をあげる
    windll.winmm.timeBeginPeriod(1)

    #----------------------------------------
    # Get status of converting
    #----------------------------------------
    sampling_start_time = time.perf_counter()
    while trial_count < len(soa_list):

        # プログラムの停止・TOJの開始　s:start q:quit b:break
        if msvcrt.kbhit() != 0:
            key = msvcrt.getch().decode()
            if key == 's':
                exp_flag = True
            elif key == 'q':
                break
            elif key == 'b':
                exp_flag = False

        #サンプリングをおこなう サンプリングレート15msec
        #サンプリングレートは最低13ms~かも
        sampling_current_time = time.perf_counter()

        sampling_elapsed_time = sampling_current_time - sampling_start_time
        #print('elapsed_time = {:.3f} Seconds'.format(sampling_elapsed_time))
        if sampling_elapsed_time >= 0.015:
            start = time.perf_counter()
            ret.value = caio.AioMultiAiEx(aio_id , AiChannels , AiData)
            end = time.perf_counter()
            #print('AioMultiAiExtime = {:.5f} ms'.format((end - start)*1000))
            if ret.value != 0:
                caio.AioGetErrorString(ret.value, err_str)
                print(f"AioMultiAiEx = {ret.value}:{err_str.value.decode('sjis')}")

            total_time += sampling_elapsed_time
            sampling_start_time = sampling_current_time
            #print("\n")

    
            if exp_flag == True:
    
                #データの収集
                for i in range(AiChannels.value):
                    volt = AiData[i]
                    resistance = volt / current
                    current_temp = (b / (math.log(resistance) + 3.8334)) - 273.15
                    temp[i] = current_temp
    
                if run_once == 0:
                    start_time = time.perf_counter()
                    run_once = 1
    
                # キャリブレーション
                if state == 1:
                    state_text = "WAITフェーズ"
                    end_time = time.perf_counter()
                    if run_once_sound == 0:
                        #print(int(soa_list[trial_count][1]))
                        winsound.Beep(2000, 100)
                        run_once_sound = 1
                    if (end_time - start_time >= 8): 
                        compare_temp = temp[2]
                        print('time = {:.5f} Seconds'.format(end_time - start_time))
                        state = 2
                        run_once = 0
                        run_once_sound = 0
                        temp_err_sum = 0
                    Vo = pi_control(temp[2], temp[0], temp_err_sum)
    
                # 提示　先行のもの    
                elif state == 2:
                    end_time = time.perf_counter()
    
                    soa = int(soa_list[trial_count][1])
                    # SOAが正の場合 触覚先行
                    if soa >= 0:
                        state_text = "BEFORE DOフェーズ 触覚"
                        ret.value = caio.AioOutputDoBit ( aio_id , 0 , 1 )
                        time.sleep(0.008)
                        ret.value = caio.AioOutputDoBit ( aio_id , 0 , 0 )
                        
                        print('time = {:.5f} Seconds'.format(end_time - start_time))
                        state = 3
                        run_once = 0
                        temp_err_sum = 0
                    # SOAが負の場合 熱先行
                
                    else:
                        state_text = "BEFORE DOフェーズ 熱"
                        if (end_time - start_time >= (abs(soa)*0.001)):
                            print('time = {:.5f} Seconds'.format(end_time - start_time))
                            state = 3
                            run_once = 0
                            temp_err_sum = 0
                        Vo = pi_control(compare_temp - 7, temp[0], temp_err_sum)
    
                elif state == 3:
                    end_time = time.perf_counter()
    
                    soa = int(soa_list[trial_count][1])
    
                    # SOAが正の場合 触覚先行
                    if soa >= 0:
                        state_text = "LATER DOフェーズ 熱"
                        if (end_time - start_time >= abs(soa)*0.001):
                            #if (end_time - start_time >= 3 - (abs(soa)*0.001)):
                            if (end_time - start_time >= remaining_time + abs(soa)*0.001):
                                print('time = {:.5f} Seconds'.format(end_time - start_time))
                                state = 4
                                run_once = 0
                                temp_err_sum = 0  
                            Vo = pi_control(compare_temp - 7, temp[0], temp_err_sum)
                                    
                    # SOAが負の場合 熱先行
                    else:
                        state_text = "LATER DOフェーズ 触覚"
                        if run_once_solenoid == 0:
                            start = time.perf_counter()
                            ret.value = caio.AioOutputDoBit ( aio_id , 0 , 1 )
                            time.sleep(0.008)
                            ret.value = caio.AioOutputDoBit ( aio_id , 0 , 0 )
                            end = time.perf_counter()
                            #print('Do_time = {} Seconds'.format(end - start))
                            
                            run_once_solenoid = 1
                        if (end_time - start_time >= remaining_time - (abs(soa)*0.001)):
                            print('time = {:.5f} Seconds'.format(end_time - start_time))
                            state = 4
                            run_once = 0
                            run_once_solenoid = 0
                            temp_err_sum = 0
                        Vo = pi_control(compare_temp - 7, temp[0], temp_err_sum)
    
                elif state == 4:
                    state_text = "ANSフェーズ"
                    end_time = time.perf_counter()
                    if run_once_sound == 0:
                        winsound.Beep(1000, 100)
                        winsound.Beep(1000, 100)
                        run_once_sound = 1
                    
                    # 階層が深くキー入力が反応しにくいため0.05秒の間隔
                    time.sleep(0.05)
                    if msvcrt.kbhit() != 0:
                        key = msvcrt.getch().decode()
                        if key == '1':
                            ans = "same time"
                            print('time = {:.5f} Seconds'.format(end_time - start_time))
                            print(ans)
                            ans_data.append([index, trial_count+1, int(soa_list[trial_count][1]), 1])
                            run_once = 0
                            run_once_sound = 0
                            temp_err_sum = 0
                            trial_count += 1
                            state = 1
                        elif key == '2':
                            ans = "not same"
                            print('time = {:.5f} Seconds'.format(end_time - start_time))
                            print(ans)
                            ans_data.append([index, trial_count+1, int(soa_list[trial_count][1]), 2])
                            run_once = 0
                            run_once_sound = 0
                            temp_err_sum = 0
                            trial_count += 1
                            state = 1

                    Vo = pi_control(temp[2], temp[0], temp_err_sum)
                
                # セーフティ
                if temp[0] <= 15 or temp[0] >= 45:
                    exp_flag = False
                    print("侵害刺激温度に達しました")
    
    
                print("\rデバイス温 {:.3f}".format(temp[0]) + "℃  " +\
                        "皮膚温変化 {:.3f}".format(temp[1]) + "℃  " +\
                        "皮膚温 {:.3f}".format(temp[2]) + "℃  " +\
                        "サンプリングレート{:.3f}".format(sampling_elapsed_time*1000) + "ミリ秒  "\
                        "トライアル{:.0f}".format(trial_count+1) + "回  " +\
                        "経過時間{:.3f}".format(total_time) + "秒  " +\
                        state_text, end = ' ', flush = True)
                
                # 出力用データ追加
                csv_data.append([index, temp[0],temp[1],temp[2], sampling_elapsed_time, trial_count+1, total_time, state_text])
                index += 1
            
            else: 
                Vo = 2.5
                ret.value = caio.AioSingleAoEx(aio_id, AoChannel, Vo)
                if ret.value != 0:
                    caio.AioGetErrorString(ret.value, err_str)
                    print(f"AioSingleAoEx = {ret.value}:{err_str.value.decode('sjis')}")
    
            
    
    # ファイル出力
    f = open('./exp/' + subject_name + '_result.csv', 'w', newline='') 
    header = ["index", "デバイス温", "皮膚温変化", "皮膚温", "サンプリングレート", "トライアル", "経過時間", "ステート"]
    writer = csv.writer(f)
    writer.writerow(header)
    result = csv_data
    writer.writerows(result)
    f.close()

    f = open('./exp/' + subject_name + '_answer.csv', 'w', newline='') 
    header = ["index", "トライアル", "SOA", "回答"]
    writer = csv.writer(f)
    writer.writerow(header)
    result = ans_data
    writer.writerows(result)
    f.close()
    
    #----------------------------------------
    # Exit the device
    #----------------------------------------
    # winidowsのOSタイマーの精度をもどす
    windll.winmm.timeEndPeriod(1)
    Vo = 2.5
    ret.value = caio.AioSingleAoEx(aio_id, AoChannel, Vo)
    if ret.value != 0:
        caio.AioGetErrorString(ret.value, err_str)
        print(f"AioSingleAoEx = {ret.value}:{err_str.value.decode('sjis')}")
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