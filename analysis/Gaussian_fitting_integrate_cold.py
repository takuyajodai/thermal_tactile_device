#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 2023

author: jodaitakuya
"""

from tkinter import filedialog
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Load custom style
style_path = Path(__file__).parent.parent / "utils" / "dsheep_white.mplstyle"
plt.style.use(str(style_path))

# CSVファイルをファイルダイアログから選択
file_paths = filedialog.askopenfilenames(
    title="Select cold CSV files",
    filetypes=(("CSV files", "*.csv"), ("All files", "*")),
)

if not file_paths:
    raise SystemExit("ファイルが選択されませんでした。")

dfs = [
    pd.read_csv(
        file,
        header=0,
        encoding="cp932",
    )
    for file in file_paths
]

analyset = np.array([-1000, -700, -500, -350, -250, -200, -150, -50, 100, 300, 600])
N = 4000
xgv = np.arange(0.0, N) - N / 2

def fitfunc(x, A, mu, sigma, B):
    return A * np.exp(-(x - mu) ** 2 / (2.0 * sigma ** 2)) + B

params_init = np.array([1.0, -250.0, 100.0, -5.0])
param_bounds = ((0.0, -np.inf, -np.inf, -np.inf), (1.0, np.inf, np.inf, np.inf))

def fit_gaussian(x_values, observations):
    obs = np.asarray(observations, dtype=float)
    mask = ~np.isnan(obs)
    x_fit = x_values[mask]
    y_fit = obs[mask]
    if x_fit.size < 3:
        raise ValueError("有効なデータ点が不足しています。")
    popt, _ = curve_fit(fitfunc, x_fit, y_fit, p0=params_init.copy(), bounds=param_bounds)
    popt[2] = np.abs(popt[2])
    Gfit = fitfunc(xgv, *popt)
    
    # フィッティング値（観測されたx値に対応する）
    y_fitted = fitfunc(x_fit, *popt)
    
    # reduced χ² の計算
    n = len(y_fit)  # データ点数
    p = len(popt)   # パラメータ数（4: A, mu, sigma, B）
    chi_squared = np.sum((y_fit - y_fitted) ** 2)
    reduced_chi_squared = chi_squared / (n - p) if (n - p) > 0 else np.nan
    
    above = np.where(Gfit >= 0.5)[0]
    if above.size > 0:
        begin = xgv[above[0]]
        end = xgv[above[-1]]
    else:
        begin = end = np.nan
    max_index = np.argmax(Gfit)
    pss = xgv[max_index]
    prob = Gfit[max_index]  # ピークの縦軸の値
    return {
        "popt": popt,
        "Gfit": Gfit,
        "begin": begin,
        "end": end,
        "pss": pss,
        "max_index": max_index,
        "prob": prob,
        "reduced_chi_squared": reduced_chi_squared,
    }

individual_label_used = False
results_list = []  # 被験者ごとの結果を保存するリスト

for path, df in zip(file_paths, dfs):
    num_tmparray = np.empty((1, 0), float)
    for soa in analyset:
        f1 = df[(df["SOA"] == soa)]
        freq = f1.iloc[:, 5].mean()
        num_tmparray = np.append(num_tmparray, freq)

    x = analyset
    observations = np.asarray(num_tmparray, dtype=float)
    filename = Path(path).name
    subject_id = Path(path).stem  # 拡張子を除いたファイル名を被験者IDとして使用
    print(f"observations ({filename}): ", observations)

    try:
        result = fit_gaussian(x, observations)
    except ValueError as exc:
        print(f"{filename}: {exc}")
        continue

    print("parameter: ", result["popt"])
    print("left: ", result["begin"])
    print("right: ", result["end"])
    window_size = np.nan
    if not np.isnan(result["begin"]) and not np.isnan(result["end"]):
        window_size = result["end"] - result["begin"]
        print("50% point: ", window_size)
    print("PSS: ", result["pss"])
    print("Prob (peak): ", result["prob"])
    print("Reduced χ²: ", result["reduced_chi_squared"])

    # 結果をリストに追加（小数点1桁まで）
    results_list.append({
        "Subject": subject_id,
        "PSS": round(result["pss"], 1) if not np.isnan(result["pss"]) else np.nan,
        "Window_size": round(window_size, 1) if not np.isnan(window_size) else np.nan,
        "Prob": round(result["prob"], 1) if not np.isnan(result["prob"]) else np.nan,
        "Reduced_chi_squared": round(result["reduced_chi_squared"], 3) if not np.isnan(result["reduced_chi_squared"]) else np.nan,
    })

    label = "individual" if not individual_label_used else None
    plt.plot(
        xgv,
        result["Gfit"],
        "-",
        color="#A4A4A4",
        linewidth=1.5,
        label=label,
        alpha=0.4,
    )
    individual_label_used = True

df_all = pd.concat(dfs, ignore_index=True)
aggregate_observations = []
for soa in analyset:
    freq = df_all[df_all["SOA"] == soa].iloc[:, 5].mean()
    aggregate_observations.append(freq)
aggregate_observations = np.asarray(aggregate_observations, dtype=float)

print("observations (aggregate): ", aggregate_observations)

aggregate_result = None
try:
    aggregate_result = fit_gaussian(analyset, aggregate_observations)
except ValueError as exc:
    print(f"aggregate: {exc}")

if aggregate_result is not None:
    print("parameter: ", aggregate_result["popt"])
    print("left: ", aggregate_result["begin"])
    print("right: ", aggregate_result["end"])
    window_size_agg = np.nan
    if not np.isnan(aggregate_result["begin"]) and not np.isnan(aggregate_result["end"]):
        window_size_agg = aggregate_result["end"] - aggregate_result["begin"]
        print("50% point: ", window_size_agg)
    print("PSS: ", aggregate_result["pss"])
    print("Prob (peak): ", aggregate_result["prob"])
    print("Reduced χ²: ", aggregate_result["reduced_chi_squared"])

    # 集約データを結果リストに追加（小数点1桁まで）
    results_list.append({
        "Subject": "aggregate",
        "PSS": round(aggregate_result["pss"], 1) if not np.isnan(aggregate_result["pss"]) else np.nan,
        "Window_size": round(window_size_agg, 1) if not np.isnan(window_size_agg) else np.nan,
        "Prob": round(aggregate_result["prob"], 1) if not np.isnan(aggregate_result["prob"]) else np.nan,
        "Reduced_chi_squared": round(aggregate_result["reduced_chi_squared"], 3) if not np.isnan(aggregate_result["reduced_chi_squared"]) else np.nan,
    })

    plt.plot(
        xgv,
        aggregate_result["Gfit"],
        "-",
        linewidth=4.0,
        color="#1D77B4",
        label="average fitting curve",
        alpha=1.0,
    )
    plt.plot(
        analyset,
        aggregate_observations,
        ".",
        color="#DB5958",
        label="average data",
        alpha=0.9,
    )

plt.xlabel("SOA(ms)", fontsize=28, fontweight="bold")
plt.ylabel("Probability of simultaneity response", fontsize=25, fontweight="bold")

plt.yticks([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])

plt.xlim([-2000, 1000])
plt.ylim([0, 1.05])

if aggregate_result is not None:
    plt.vlines(
        aggregate_result["pss"],
        0,
        aggregate_result["Gfit"][aggregate_result["max_index"]],
        color="#1D77B4",
        linestyles="dashed",
        label="average PSS",
    )
    if not np.isnan(aggregate_result["begin"]) and not np.isnan(aggregate_result["end"]):
        plt.fill_between(
            xgv,
            aggregate_result["Gfit"],
            where=(xgv >= aggregate_result["begin"]) & (xgv <= aggregate_result["end"]),
            color="#1D77B4",
            alpha=0.2,
        )

plt.legend(fontsize=22)
plt.tick_params(labelsize=22)

plt.xticks(fontweight="bold")
plt.yticks(fontweight="bold")

plt.tick_params(axis="x", pad=15)
plt.tick_params(axis="y", pad=10)

plt.tight_layout()
plt.show()

# 結果をCSVファイルに保存
if results_list:
    results_df = pd.DataFrame(results_list)
    # ファイル保存ダイアログを表示
    output_path = filedialog.asksaveasfilename(
        title="Save results as CSV",
        defaultextension=".csv",
        filetypes=(("CSV files", "*.csv"), ("All files", "*")),
    )
    if output_path:
        results_df.to_csv(output_path, index=False, encoding="utf-8-sig")
        print(f"\n結果を保存しました: {output_path}")
        print("\n保存されたデータ:")
        print(results_df.to_string(index=False))
    else:
        print("\nCSVファイルの保存がキャンセルされました。")
else:
    print("\n保存する結果がありませんでした。")
