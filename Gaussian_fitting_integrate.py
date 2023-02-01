#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 2023

author: jodaitakuya
"""

from tkinter import filedialog
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import math
plt.style.use("dsheep_white")

#csv 11こ
files = ['./data/1.csv', './data/3.csv','./data/4.csv','./data/5.csv','./data/6.csv','./data/7.csv','./data/8.csv','./data/9.csv','./data/10.csv','./data/11.csv','./data/12.csv','./data/all-no2.csv']

dfs = []

for i,file in enumerate(files):
    df = pd.read_csv(file, 
        header = 0,
        skiprows = [1, 2],
        encoding='cp932',
        )
    dfs.append(df)


for i,df in enumerate(dfs):
    tmpData= np.empty((0,6), int)

    analyset = np.array([-1000,-700,-500,-350,-250,-200,-150,-50,100,300,600])

    num_tmparray=np.empty((1,0),float);
    hh=analyset.size

    # 割合計算
    for r in range(hh):
        f1=df[(df['SOA']==analyset[r])]   # SOAはデータの5行目，これとSOAの値がマッチする値を取り出す
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
    N = 2600 #データ点数 1msにつき1点くらいでいいのでは？ 適当
    xgv = np.arange(0.0, N) - N/2 #軸の設定
    # フィッティングする関数形の定義
    def fitfunc(x, A, mu, sigma, B):
        return A*np.exp(-(x-mu)**2/(2.0*sigma**2)) + B

    # フィッティングの初期パラメタ これ最適化しないといけない (A, mu, sigma, B)
    params_init = np.array([1.0, -250.0, 100.0, -5.0])
    param_bounds = ((0.0, -np.inf, -np.inf, -np.inf), (1.0, np.inf, np.inf, np.inf)) # bounds for parameter

    # 最適化実行 popt: 推定されたパラメタ pcov: 共分散→平方根で標準誤差
    popt, pcov = curve_fit(fitfunc, x, observations, p0 = params_init, bounds=param_bounds)
    popt[2] = np.abs(popt[2]) #分散は正でいい
    #print("parameter: ", popt)

    # 最適化されたパラメタを使ってフィット関数を作成
    Gfit = fitfunc(xgv, *popt)
    #plt.plot(xgv, Gfit, 'r-', label = 'fitting curve') #フィッティング・プロット
    
    if i == len(dfs) - 1:
        plt.plot(xgv, Gfit, '-', linewidth = 4.0, color='#DB5958', label = 'average fitting curve', alpha=1.0) #フィッティング・プロット
        plt.plot(x, num_tmparray, '.', color='#1D77B4', label = 'average data', alpha=0.9) 
    else:
        if i == 0:
            plt.plot(xgv, Gfit, '-', color='#A4A4A4', label = 'individual', alpha=0.4) #フィッティング・プロット
        else: 
            plt.plot(xgv, Gfit, '-', color='#A4A4A4', alpha=0.4) #フィッティング・プロット

    
    # 同時性の窓の検出 Full Width Half Maximum 
    fwhm = 2 * (2 * math.log(2)) ** 0.5 * popt[2] #FWHM=2*(2*ln2)^0.5 *SD
    # 50%幅の導出
    point50 = list(filter(lambda x: 0.5 <= x, list(Gfit)))
    if point50:
        begin = xgv[list(Gfit).index(point50[0])]
        end = xgv[list(Gfit).index(point50[-1])]
    # PSSの導出
    max_index = np.argmax(Gfit)
    pss = xgv[max_index]

    print(begin)
    print(end)

    #print("FWHM: ", fwhm)
    #print("SD: ", abs(popt[2]))
    #if point50:
    #   print("50% point: ", end-begin)
    print("PSS: ", pss)
    


#plt.plot(xgv, Gfit, 'r-', label = 'fitting curve') #フィッティング・プロット

# グラフ表示の設定
plt.xlabel('SOA(ms)', fontsize=14) #x軸の名前とフォントサイズ
plt.ylabel('Probability of simultaneity response', fontsize=14) #y軸の名前とフォントサイズ
#plt.legend(loc='proportion of simutanious') #ラベルを右上に記載

plt.yticks([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])

plt.xlim([-1200,1000])
plt.ylim([0,1.05])

plt.vlines(pss, 0, Gfit[max_index], color='#DB5958', linestyles='dashed', label='average PSS')


#plt.plot(xgv, Gfit, '-', color='#DB5958', label = 'fitting curve', alpha=1.0) #フィッティング・プロット

plt.fill_between(xgv, Gfit, where=(xgv >= begin) & (xgv <= end), alpha=0.2)
plt.legend()

#plt.savefig("SJ.png", format="png", dpi=600)
plt.show()
#plt.savefig('plot.png')
#plt.close()

