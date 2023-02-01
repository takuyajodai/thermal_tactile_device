#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 29 2023

@author: jodaitakuya
"""

from tkinter import filedialog
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import math
import codecs

plt.style.use("dsheep_white")


filename="/Users/JodaiTakuya/Library/Mobile Documents/com~apple~CloudDocs/study/Ho lab/データ/exp_raw/3_KT_2_result.csv"

x_name = "index"
y_name_list = ['device_temp','device&skin_temp','skin_temp']


df = pd.read_csv(filename, 
  header = 0,
  skiprows = [1, 2],
  encoding='cp932',
  )

#print(df)

x_list = df[x_name].values.tolist()
y_list1 = df[y_name_list[0]].values.tolist()
y_list2 = df[y_name_list[1]].values.tolist()
y_list3 = df[y_name_list[2]].values.tolist()
#print(x_list)

#plt.plot(xgv, Gfit, 'r-', label = 'fitting curve') #フィッティング・プロット

# グラフ表示の設定
plt.xlabel('index', fontsize=14) #x軸の名前とフォントサイズ
plt.ylabel('temperature (°C)', fontsize=14) #y軸の名前とフォントサイズ
#plt.legend(loc='proportion of simutanious') #ラベルを右上に記載

plt.xlim([1000,2000])
plt.ylim([24,33])


plt.scatter(x_list, y_list1, s=30, color='#1D77B4', label = 'device temp', alpha=0.3) # 散布図a
plt.scatter(x_list, y_list2, s=30, color='#DB5958', label = 'device&skin temp', alpha=0.3) # 散布図
plt.scatter(x_list, y_list3, s=30, color='#45B28B', label = 'skin temp', alpha=0.3) # 散布図
#plt.fill_between(xgv, Gfit, where=(xgv >= begin) & (xgv <= end), alpha=0.2)
plt.legend()

#plt.savefig("SJ.png", format="png", dpi=600)
plt.show()

#plt.savefig('temperature.png')
plt.close()


