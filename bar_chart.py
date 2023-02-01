#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 2023

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


filename='./data/window.csv'

df = pd.read_csv(filename, 
  header = 0,
  #skiprows = [1],
  encoding='cp932',
  )

print(df)

mean_FWHM = df['FWHM'].mean() 
mean_SD = df['SD'].mean() 
mean_S_window = df['S_window'].mean() 

print (mean_FWHM)
print (mean_SD)
print (mean_S_window)

sem_FWHM = df["FWHM"].sem()
sem_SD = df["SD"].sem()
sem_S_window = df['S_window'].sem()
print (sem_FWHM)
print (sem_SD)
print (sem_S_window)

x = np.array(['FWHM', 'SD', '50% window'])
y = np.array([mean_FWHM, mean_SD, mean_S_window])


x_position = np.arange(len(x))

err = [sem_FWHM, sem_SD, sem_S_window]


plt.barh(x_position, y, height= 0.5, tick_label=x, xerr=err, capsize=10, color='#45B28B', alpha=0.9)

# グラフ表示の設定
plt.xlabel('window size(ms)', fontsize=14) #x軸の名前とフォントサイズ
plt.legend()
plt.ylabel('types of window', fontsize=14) #y軸の名前とフォントサイズ
plt.legend()

#plt.savefig("SJ.png", format="png", dpi=600)
plt.show()

#plt.savefig('temperature.png')
#plt.close()


