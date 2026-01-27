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
import sys
import msvcrt
import caio
import math
import numpy as np
import matplotlib.pyplot as plt
import time
import csv
import winsound
from ctypes import windll
from pathlib import Path

# Custom modules
from SOA_generator import generate_soa_list

# Constants
AI_ERR_HAPPENED     = 2
DATA_MAX = 16000                                # The size of converted data
AoChannel = 0                                   # 使用する出力チャンネル

# temp cal
current = 0.000487
b = 3889
# parameter
ki = -0.0003
kp = -0.5

def initialize_device(device_name="AIO001"):
    """
    デバイスの初期化と基本設定を行う。

    Args:
        device_name (str): 使用するデバイスの名前。

    Returns:
        tuple: 初期化された値（aio_id, ret, err_str, AiChannels, AiData）。
    """
    #----------------------------------------
    # Declare variables
    #----------------------------------------
    ret = ctypes.c_long()                           # Return values of functions
    aio_id = ctypes.c_short()                       # device id
    err_str = ctypes.create_string_buffer(256)      # Error string
    AiDataType = ctypes.c_float * DATA_MAX          # Create the array type (Converted data)
    AiData = AiDataType()                           # Converted data
    AiChannels = ctypes.c_short()                   # Number of the used channels

    # デバイス初期化
    ret.value = caio.AioInit(device_name.encode(), ctypes.byref(aio_id))
    if ret.value != 0:
        caio.AioGetErrorString(ret.value, err_str)
        print(f"AioInit エラー: {ret.value} - {err_str.value.decode('sjis')}")
        sys.exit()

    # デバイスリセット
    ret.value = caio.AioResetDevice(aio_id)
    if ret.value != 0:
        caio.AioGetErrorString(ret.value, err_str)
        print(f"AioResetDevice エラー: {ret.value} - {err_str.value.decode('sjis')}")
        sys.exit()

    # チャンネル設定
    AiChannels = ctypes.c_short()
    aiChannels = 3
    ret.value = caio.AioSetAiChannels(aio_id, aiChannels)
    if ret.value != 0:
        caio.AioGetErrorString(ret.value, err_str)
        print(f"AioSetAiChannels エラー: {ret.value} - {err_str.value.decode('sjis')}")
        sys.exit()

    ret.value = caio.AioGetAiChannels(aio_id, ctypes.byref(AiChannels))

    # 入力範囲設定
    aiRange = 0  # ±10V
    ret.value = caio.AioSetAiRangeAll(aio_id, aiRange)
    if ret.value != 0:
        caio.AioGetErrorString(ret.value, err_str)
        print(f"AioSetAiRangeAll エラー: {ret.value} - {err_str.value.decode('sjis')}")
        sys.exit()

    # 出力範囲設定
    aoRange = 0  # 0～5V
    ret.value = caio.AioSetAoRangeAll(aio_id, aoRange)
    if ret.value != 0:
        caio.AioGetErrorString(ret.value, err_str)
        print(f"AioSetAoRangeAll エラー: {ret.value} - {err_str.value.decode('sjis')}")
        sys.exit()

    # メモリリセット
    ret.value = caio.AioResetAiMemory(aio_id)
    if ret.value != 0:
        caio.AioGetErrorString(ret.value, err_str)
        print(f"AioResetAiMemory エラー: {ret.value} - {err_str.value.decode('sjis')}")
        sys.exit()

    return {
        "aio_id": aio_id,
        "ret": ret,
        "err_str": err_str,
        "AiChannels": AiChannels, 
        "AiData": AiData,
    }

def write_csv(filename, header, data):
    """
    CSVファイルにデータを書き込む。

    Args:
        filename (str): ファイル名。
        header (list): ヘッダー行。
        data (list): 書き込むデータ。
    """
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(data)


#================================================================
# Main function
#================================================================
def main():
    # 初期設定
    device = initialize_device()

    # デバイス情報を取得
    aio_id = device["aio_id"]
    ret = device["ret"] 
    err_str = device["err_str"]
    AiChannels = device["AiChannels"]
    AiData = device["AiData"]

    #----------------------------------------
    # Declare variables
    #----------------------------------------

    temp = []                                       # temp[0] : device temp, temp[1] : skin temp change, temp[2] : skin_temp
    exp_flag = False                                # セッション中か
    state = 1
    run_once = 0
    run_once_sound = 0
    tactile_triggered = False                       # 触覚刺激が提示済みか
    run_once_solenoid = 0
    trial_count = 0                                 # 一試行ごとにインクリメント
    state_text = ""
    total_time = 0
    compare_temp = 33                               # Waitの最初に皮膚温の代表値として-7℃のために取得
    stimulus_temp = -7                               # -7 もしくは+7℃


    csv_data = [[]]
    ans_data = [[]]
    index = 0

    remaining_time = 5


    

    # PI control
    temp_err_sum = 0


    #----------------------------------------
    # Declare function
    #----------------------------------------
    modes = {
        "rapid": {"voltage_range": None}, # 急速モード: 制限なし(0~5v)
        "smooth": {"voltage_range": 1.0}, #緩やかモード: ±1.0v (2.5±1.0v)
    }

    def pi_control(aimed_temp, current_temp, temp_err_sum, mode="rapid"):
        # PIコントロール

        # モード設定を取得
        if mode not in modes:
            raise ValueError(f"未知のモード: {mode}")
        voltage_range = modes[mode]["voltage_range"]

        # 温度誤差を計算
        temp_err = float(aimed_temp) - current_temp
        temp_err_sum += temp_err # 時間積分（積分項）

        # PI制御式で出力電圧を計算
        Vo = (kp * temp_err) + (ki * temp_err_sum) + 2.5

        # 電圧の範囲を制限（例: 0～5V）
        if voltage_range is not None:
            base_voltage = 2.5
            Vo = max(base_voltage - voltage_range, min(Vo, base_voltage + voltage_range))
        else:
            # 急速モードではフルレンジ(0~5v)を使用
            Vo = max(0, min(Vo, 5))
        
        # DAQデバイスに出力電圧を送信
        ret.value = caio.AioSingleAoEx(aio_id, AoChannel, Vo)


        if ret.value != 0:
            caio.AioGetErrorString(ret.value, err_str)
            print(f"AioSingleAoEx = {ret.value}:{err_str.value.decode('sjis')}")
        return Vo, temp_err_sum

    

    soa_list = generate_soa_list()
    practice_list = [-1500, 1500, -1500, 1500, -1500, 1500, -1500, 1500]
    #soa_list = [[i, practice_list[i]] for i in range(len(practice_list))]
    #temp_list = [-1500,-1000,-700, -300, 0, 300, 400]
    #soa_list = [[i, temp_list[i]] for i in range(len(temp_list))]

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
            ret.value = caio.AioMultiAiEx(aio_id , AiChannels , AiData)
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
                        winsound.Beep(2000, 100)
                        run_once_sound = 1
                    if end_time - start_time >= 9: 
                        compare_temp = temp[2]
                        print('time = {:.5f} Seconds'.format(end_time - start_time))
                        state = 2
                        run_once = 0
                        run_once_sound = 0
                    Vo, temp_err_sum = pi_control(temp[2], temp[0], temp_err_sum, mode="rapid")
    
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

                    # SOAが負の場合 熱先行
                    else:
                        state_text = "BEFORE DOフェーズ 熱"
                        # SOA時間分経過したら
                        if (end_time - start_time >= (abs(soa)*0.001)):
                            print('time = {:.5f} Seconds'.format(end_time - start_time))
                            state = 3
                            run_once = 0
                            print('達してない刺激 = {:.3f} ℃'.format(compare_temp - current_temp))
                        else:
                            Vo, temp_err_sum  = pi_control(compare_temp + stimulus_temp, temp[0], temp_err_sum, mode="rapid")
    
                elif state == 3:
                    end_time = time.perf_counter()
    
                    soa = int(soa_list[trial_count][1])
    
                    # SOAが正の場合 触覚先行
                    if soa >= 0:
                        state_text = "LATER DOフェーズ 熱"
                        """
                        # SOA時間分経過したら
                        if (end_time - start_time >= abs(soa)*0.001):
                            if (end_time - start_time >= remaining_time + abs(soa)*0.001):
                                print('time = {:.5f} Seconds'.format(end_time - start_time))
                                state = 4
                                run_once = 0
                                print('達してない刺激 = {:.3f} ℃'.format(compare_temp - current_temp))
                        else:
                            Vo, temp_err_sum  = pi_control(compare_temp + stimulus_temp, temp[0], temp_err_sum, mode="rapid")
                                    
                        """
                        # SOA時間分経過したら
                        if (end_time - start_time >= abs(soa)*0.001):
                            # 提示時間が経過したら次の状態へ
                            if (end_time - start_time >= remaining_time - abs(soa)*0.001):
                                print('time = {:.5f} Seconds'.format(end_time - start_time))
                                state = 4
                                run_once = 0
                            else:
                                Vo, temp_err_sum  = pi_control(compare_temp + stimulus_temp, temp[0], temp_err_sum, mode="rapid")
                        else:
                            Vo, temp_err_sum  = pi_control(temp[2], temp[0], temp_err_sum, mode="rapid")
                                    
                    # SOAが負の場合 熱先行
                    else:
                        state_text = "LATER DOフェーズ 触覚"
                        if not tactile_triggered:
                            ret.value = caio.AioOutputDoBit ( aio_id , 0 , 1 )
                            time.sleep(0.008)
                            ret.value = caio.AioOutputDoBit ( aio_id , 0 , 0 )
                            tactile_triggered = True

                        # 提示時間が経過したら次の状態へ
                        if (end_time - start_time >= remaining_time - (abs(soa)*0.001)):
                            print('time = {:.5f} Seconds'.format(end_time - start_time))
                            state = 4
                            run_once = 0
                            temp_err_sum = 0
                        else:
                            Vo, temp_err_sum = pi_control(compare_temp + stimulus_temp, temp[0], temp_err_sum, mode="rapid")
    
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
                        if key in ['1','2']:
                            ans = "same time" if key == '1' else "not same"
                            print('time = {:.5f} Seconds'.format(end_time - start_time))
                            print(ans)
                            ans_data.append([index, trial_count+1, int(soa_list[trial_count][1] + 117), 1])
                            run_once = 0
                            run_once_sound = 0
                            temp_err_sum = 0
                            trial_count += 1
                            state = 1
                            tactile_triggered = False

                    Vo, temp_err_sum = pi_control(temp[2], temp[0], temp_err_sum, mode="rapid")
                
                # セーフティ
                if temp[0] <= 15 or temp[0] >= 45:
                    exp_flag = False
                    print("侵害刺激温度に達しました")
    
    
                print("\rVo {:.3f}".format(Vo) + "V  " +\
                        "デバイス温 {:.3f}".format(temp[0]) + "℃  " +\
                        "デバイス・皮膚温 {:.3f}".format(temp[1]) + "℃  " +\
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
    base_dir = Path(__file__).parent
    out_dir = base_dir / "spacial_exp_cool"
    result_path = out_dir / f"{subject_name}_result.csv"
    answer_path = out_dir / f"{subject_name}_answer.csv"

    write_csv(
        result_path,
        ["index", "device_temp", "device&skin_temp", "skin_temp", "sampling_rate", "number_of_trial", "time", "state"],
        csv_data,
    )

    write_csv(
        answer_path,
        ["index", "number_of_trial", "SOA", "answer"],
        ans_data,
    )

    """
    f = open('./spacial_exp_cool/' + subject_name + '_result.csv', 'w', newline='') 
    header = ["index", "device_temp", "device&skin_temp", "skin_temp", "sampling_rate", "number_of_trial", "time", "state"]
    writer = csv.writer(f)
    writer.writerow(header)
    result = csv_data
    writer.writerows(result)
    f.close()

    f = open('./spacial_exp_cool/' + subject_name + '_answer.csv', 'w', newline='') 
    header = ["index", "number_of_trial", "SOA", "answer"]
    writer = csv.writer(f)
    writer.writerow(header)
    result = ans_data
    writer.writerows(result)
    f.close()
    """

    
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