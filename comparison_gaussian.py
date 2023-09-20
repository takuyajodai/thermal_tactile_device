#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 5 20:56:27 2023

@author : jodaitakuya
"""

from tkinter import filedialog
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import math
plt.style.use("dsheep_white")


filename=filedialog.askopenfilenames()
f_num=len(filename)


tmpData= np.empty((0,6), int)
idx=0
for t in range(f_num):
    f=open(filename[t], 'r')
    line = f.readline() # 1行を文字列として読み込む(改行文字も含まれる) １行読み飛ばす
    line = f.readline()
    while line:
        #print line
        hoge = line.rstrip().split(',')
        tmpData=np.append(tmpData,[np.array([idx,int(hoge[1]),int(hoge[2]),int(hoge[3]),int(hoge[4]),int(hoge[5])])],axis=0)
        idx=idx+1
        line = f.readline()
    f.close

ff=pd.DataFrame(tmpData)    #csvの行列そのもの (ヘッダー以外)

#analyset = np.array([-1000,-700,-500,-350,-250,-200,-150,-50,100,300,600])
analyset = np.array([-2000,-1500,-1100,-800,-600,-500,-400,-200,100,500,1000])

num_tmparray=np.empty((1,0),float);
hh=analyset.size

# 割合計算
for r in range(hh):
    f1=ff[(ff.loc[:,4]==analyset[r])]   # SOAはデータの5行目，これとSOAの値がマッチする値を取り出す
    freq=f1.iloc[:,5].mean()            # Ansで平均とる
    num_tmparray = np.append(num_tmparray,freq) # 空白配列に入れていく
    #print(f1)
    
print(num_tmparray)
x=analyset

observations = num_tmparray
#data_sessions=np.c_[x,observations]

#############################
#ここからfitting
#############################
N = 4000 #データ点数 1msにつき1点くらいでいいのでは？ 適当
xgv = np.arange(0.0, N) - N/2 #軸の設定
# フィッティングする関数形の定義
def fitfunc(x, A, mu, sigma, B):
    return A*np.exp(-(x-mu)**2/(2.0*sigma**2)) + B

# フィッティングの初期パラメタ これ最適化しないといけない (A, mu, sigma, B)
params_init = np.array([1.0, -500.0, 100.0, -5.0])
param_bounds = ((0.0, -np.inf, -np.inf, -np.inf), (1.0, np.inf, np.inf, np.inf)) # bounds for parameter

# 最適化実行 popt: 推定されたパラメタ pcov: 共分散→平方根で標準誤差
popt, pcov = curve_fit(fitfunc, x, observations, p0 = params_init, bounds=param_bounds)
popt[2] = np.abs(popt[2]) #分散は正でいい
print("parameter: ", popt)

# 最適化されたパラメタを使ってフィット関数を作成
Gfit = fitfunc(xgv, *popt)
#plt.plot(xgv, Gfit, 'r-', label = 'fitting curve') #フィッティング・プロット

# 同時性の窓の検出 Full Width Half Maximum 
fwhm = 2 * (2 * math.log(2)) ** 0.5 * popt[2] #FWHM=2*(2*ln2)^0.5 *SD
# 50%幅の導出
point50 = list(filter(lambda x: 0.5 <= x, list(Gfit)))
if point50:
    begin = xgv[list(Gfit).index(point50[0])]
    end = xgv[list(Gfit).index(point50[-1])]
    print(begin)
    print(end)
# PSSの導出
max_index = np.argmax(Gfit)
pss = xgv[max_index]
print("PSSの割合点", Gfit[max_index])

#print(begin)
#print(end)

print("FWHM: ", fwhm)
print("SD: ", abs(popt[2]))
if point50:
    print("warm 50% point: ", end-begin)
print("warm PSS: ", pss)


########################
########################

filename2=filedialog.askopenfilenames()
f_num2=len(filename2)


tmpData2= np.empty((0,6), int)
idx2=0
for t in range(f_num2):
    f=open(filename2[t], 'r')
    line = f.readline() # 1行を文字列として読み込む(改行文字も含まれる) １行読み飛ばす
    line = f.readline()
    while line:
        #print line
        hoge = line.rstrip().split(',')
        tmpData2=np.append(tmpData2,[np.array([idx2,int(hoge[1]),int(hoge[2]),int(hoge[3]),int(hoge[4]),int(hoge[5])])],axis=0)
        idx2=idx2+1
        line = f.readline()
    f.close

ff2=pd.DataFrame(tmpData2)    #csvの行列そのもの (ヘッダー以外)

analyset2 = np.array([-1000,-700,-500,-350,-250,-200,-150,-50,100,300,600])
#analyset = np.array([-2000,-1500,-1100,-800,-600,-500,-400,-200,100,500,1000])

num_tmparray2=np.empty((1,0),float);
hh2=analyset2.size

# 割合計算
for r in range(hh2):
    f1=ff2[(ff2.loc[:,4]==analyset2[r])]   # SOAはデータの5行目，これとSOAの値がマッチする値を取り出す
    freq=f1.iloc[:,5].mean()            # Ansで平均とる
    num_tmparray2 = np.append(num_tmparray2,freq) # 空白配列に入れていく
    #print(f1)
    
print(num_tmparray2)
x2=analyset2

observations = num_tmparray2
#data_sessions=np.c_[x,observations]

#############################
#ここからfitting
#############################
N = 2600 #データ点数 1msにつき1点くらいでいいのでは？ 適当
xgv2 = np.arange(0.0, N) - N/2 #軸の設定
# フィッティングする関数形の定義
def fitfunc(x, A, mu, sigma, B):
    return A*np.exp(-(x-mu)**2/(2.0*sigma**2)) + B

# フィッティングの初期パラメタ これ最適化しないといけない (A, mu, sigma, B)
params_init = np.array([1.0, -250.0, 100.0, -5.0])
param_bounds = ((0.0, -np.inf, -np.inf, -np.inf), (1.0, np.inf, np.inf, np.inf)) # bounds for parameter

# 最適化実行 popt: 推定されたパラメタ pcov2: 共分散→平方根で標準誤差
popt2, pcov2 = curve_fit(fitfunc, x2, observations, p0 = params_init, bounds=param_bounds)
popt2[2] = np.abs(popt2[2]) #分散は正でいい
print("parameter: ", popt2)

# 最適化されたパラメタを使ってフィット関数を作成
Gfit2 = fitfunc(xgv2, *popt2)
#plt.plot(xgv, Gfit2, 'r-', label = 'fitting curve') #フィッティング・プロット

# 同時性の窓の検出 Full Width Half Maximum 
fwhm2 = 2 * (2 * math.log(2)) ** 0.5 * popt2[2] #FWHM=2*(2*ln2)^0.5 *SD
# 50%幅の導出
point50_2 = list(filter(lambda x: 0.5 <= x, list(Gfit2)))
if point50_2:
    begin2 = xgv2[list(Gfit2).index(point50_2[0])]
    end2 = xgv2[list(Gfit2).index(point50_2[-1])]
    print(begin2)
    print(end2)
# PSSの導出
max_index2 = np.argmax(Gfit2)
pss2 = xgv2[max_index2]
print("PSSの割合点", Gfit2[max_index2])

#print(begin2)
#print(end2)

print("FWHM: ", fwhm2)
print("SD: ", abs(popt2[2]))
if point50:
    print("cool 50% point: ", end2-begin2)
print("cool PSS: ", pss2)



#plt.plot(xgv, Gfit, 'r-', label = 'fitting curve') #フィッティング・プロット

# グラフ表示の設定
plt.xlabel('SOA(ms)', fontsize=22) #x軸の名前とフォントサイズ
plt.ylabel('Probability of simultaneity response', fontsize=22) #y軸の名前とフォントサイズ
#plt.legend(loc='proportion of simutanious') #ラベルを右上に記載

plt.yticks([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])

plt.xlim([-2000,1000])
plt.ylim([0,1.05])

plt.vlines(pss, 0, Gfit[max_index], color='#DB5958', linestyles='dashed', label='warm_PSS')
plt.vlines(pss2, 0, Gfit2[max_index2], color='#2B42A8', linestyles='dashed', label='cold_PSS')

plt.plot(x, num_tmparray, '.', color='#EF6056', label = 'warm_data', alpha=0.9) 
plt.plot(x2, num_tmparray2, '.', color='#4759D9', label = 'cold_data', alpha=0.9) 
plt.plot(xgv, Gfit, '-', color='#DB5958', label = 'warm_fitting curve', alpha=1.0) #フィッティング・プロット
plt.plot(xgv2, Gfit2, '-', color='#4759D9', label = 'cold_fitting curve', alpha=1.0) #フィッティング・プロット
if point50:
    plt.fill_between(xgv, Gfit, where=(xgv >= begin) & (xgv <= end), alpha=0.2)
if point50_2:
    plt.fill_between(xgv2, Gfit2, where=(xgv2 >= begin2) & (xgv2 <= end2), alpha=0.2)
plt.legend(fontsize=18)
plt.tick_params(labelsize=20)

#plt.savefig("SJ.png", format="png", dpi=600)
plt.show()
plt.savefig('plot_warm.png')
#plt.close()

