#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 2023

author: jodaitakuya

概要:
このスクリプトは、複数のCSVファイルから空間的寒冷刺激（spatial cold）のデータを読み込み、
ガウシアン関数でフィッティングを行い、以下の指標を計算します：
- PSS (Point of Subjective Simultaneity)
- Window size (50% point)
- Prob (ピークの縦軸の値)
- AIC/BIC (モデル選択指標)
- Reduced χ² (適合度指標)
- 擬似R² (McFadden's pseudo R²)

データ形式:
- CSVファイルの列5（インデックス5）に0/1コード化された回答が含まれている必要があります
- 0: 非同時性, 1: 同時性と判断

出力:
- グラフ: フィッティング曲線とデータポイントの可視化
- CSV: 各被験者および集約データの結果
"""

from tkinter import filedialog
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.special import xlogy, expit, logit

# Load custom style
style_path = Path(__file__).parent.parent / "utils" / "dsheep_white.mplstyle"
plt.style.use(str(style_path))

# =============================================================================
# データ読み込み
# =============================================================================

# CSVファイルをファイルダイアログから選択（複数選択可）
file_paths = filedialog.askopenfilenames(
    title="Select spatial cold CSV files",
    filetypes=(("CSV files", "*.csv"), ("All files", "*")),
)

if not file_paths:
    raise SystemExit("ファイルが選択されませんでした。")

# 選択された全てのCSVファイルを読み込む
dfs = [
    pd.read_csv(
        file,
        header=0,
        encoding="cp932",
    )
    for file in file_paths
]

# =============================================================================
# 解析パラメータの設定
# =============================================================================

# 解析対象のSOA（Stimulus Onset Asynchrony）値（ms単位）
analyset = np.array([-2000, -1500, -1200, -1000, -850, -700, -550, -400, -200, 100, 600])

# フィッティング曲線の描画用グリッド（詳細な曲線を描くため）
N = 4000  # データ点数
xgv = np.arange(0.0, N) - N / 2  # -2000から2000までの範囲

def fitfunc(x, A_raw, mu, log_sigma, B_raw):
    """Reparameterized gaussian-like probability function.
    Parameters are in unconstrained/raw space: A_raw and B_raw are mapped via sigmoid (expit)
    so that B in (0,1) and A in (0, 1-B). sigma is parameterized via log_sigma to ensure sigma>0.
    This guarantees the model output stays in [0,1].
    """
    B = expit(B_raw)                       # 0..1
    A = (1.0 - B) * expit(A_raw)           # 0..1-B
    sigma = np.exp(log_sigma)
    return A * np.exp(-(x - mu) ** 2 / (2.0 * sigma ** 2)) + B

def metrics_binomial(k, n, x_fit, popt, fitfunc):
    """
    二項モデルに基づく適合度指標を計算する関数
    
    成功数kと試行数nを使用して、正確な二項分布に基づく統計指標を計算します。
    これにより、確率データのフィッティングの適合度を適切に評価できます。
    
    Parameters:
    -----------
    k : array-like
        各SOAでの成功数（同時性と判定した回数）
    n : array-like
        各SOAでの試行数（総回答数）
    x_fit : array-like
        フィッティングに使用したSOA値の配列
    popt : array-like
        フィッティングされたパラメータ（生のパラメータ空間）
    fitfunc : function
        フィッティング関数（fitfunc(x, *popt)で予測値を計算）
        
    Returns:
    --------
    dict
        以下のキーを含む辞書：
        - loglik: 対数尤度（フィッティングモデル）
        - loglik_null: 対数尤度（ヌルモデル：定数確率）
        - AIC: Akaike Information Criterion（小さいほど良い）
        - BIC: Bayesian Information Criterion（小さいほど良い）
        - chi2: Pearsonカイ二乗統計量
        - reduced_chi2: 正規化されたカイ二乗（自由度で割った値、1に近いほど良い）
        - df: 自由度（データ点数 - パラメータ数）
        - pseudoR2_mcf: McFaddenの擬似R²（0-1の範囲、1に近いほど良い）
        - deviance_R2: デビアンスベースのR²（0-1の範囲、1に近いほど良い）
        - deviance: デビアンス（モデルと飽和モデルの差）
        - reduced_deviance: 正規化されたデビアンス
        - rmse: Root Mean Squared Error（小さいほど良い）
        - mae: Mean Absolute Error（小さいほど良い）
    """
    # データの型変換と準備
    k = np.asarray(k, dtype=float)
    n = np.asarray(n, dtype=float)
    
    # フィッティングモデルによる予測確率（0-1の範囲にクリッピング）
    p_hat = np.clip(fitfunc(x_fit, *popt), 1e-12, 1 - 1e-12)
    
    # =====================================================================
    # 対数尤度の計算（二項分布に基づく）
    # =====================================================================
    # フィッティングモデルの対数尤度
    # log L = Σ[k*log(p) + (n-k)*log(1-p)]
    ll = np.sum(xlogy(k, p_hat) + xlogy(n - k, 1 - p_hat))
    
    # ヌルモデル（定数確率モデル）の対数尤度
    # 全データの平均成功率を確率として使用
    p0 = np.sum(k) / np.sum(n) if np.sum(n) > 0 else np.nan
    ll_null = np.sum(xlogy(k, p0) + xlogy(n - k, 1 - p0)) if np.sum(n) > 0 else np.nan
    
    # =====================================================================
    # モデル選択指標（AIC/BIC）
    # =====================================================================
    p_param = len(popt)  # パラメータ数
    N = len(k)  # データ点数
    # AIC = 2k - 2ln(L) （k: パラメータ数, L: 尤度）
    AIC = 2 * p_param - 2 * ll
    # BIC = k*ln(n) - 2ln(L) （n: データ点数）
    BIC = p_param * np.log(N) - 2 * ll
    
    # =====================================================================
    # Pearsonカイ二乗統計量
    # =====================================================================
    # χ² = Σ[(k - n*p)² / (n*p*(1-p))]
    # 分母が0にならないようにクリッピング
    denom = n * p_hat * (1 - p_hat)
    denom = np.clip(denom, 1e-12, None)
    chi2 = np.sum((k - n * p_hat) ** 2 / denom)
    df = N - p_param  # 自由度
    reduced_chi2 = chi2 / df if df > 0 else np.nan  # 正規化されたカイ二乗
    
    # =====================================================================
    # 擬似R²（McFadden's pseudo R²）
    # =====================================================================
    # R²_mcf = 1 - (LL_model / LL_null)
    # 0-1の範囲で、1に近いほど良い適合
    pseudoR2_mcf = 1 - (ll / ll_null) if ll_null != 0 else np.nan
    
    # =====================================================================
    # デビアンスベースのR²
    # =====================================================================
    # 飽和モデル（各データ点で観測された確率を完全に説明するモデル）の尤度
    p_sat = np.clip(k / n, 1e-12, 1 - 1e-12)
    ll_sat = np.sum(xlogy(k, p_sat) + xlogy(n - k, 1 - p_sat))
    
    # デビアンス = -2 * (LL_model - LL_saturated)
    dev_model = -2 * (ll - ll_sat)  # モデルのデビアンス
    dev_null = -2 * (ll_null - ll_sat)  # ヌルモデルのデビアンス
    
    # デビアンスベースのR² = 1 - (dev_model / dev_null)
    deviance_R2 = 1 - dev_model / dev_null if dev_null != 0 else np.nan
    reduced_deviance = dev_model / df if df > 0 else np.nan  # 正規化されたデビアンス
    
    # =====================================================================
    # 残差に関する指標（RMSE、MAE）
    # =====================================================================
    obs_prop = k / n  # 観測された成功率
    rmse = np.sqrt(np.mean((obs_prop - p_hat) ** 2))  # Root Mean Squared Error
    mae = np.mean(np.abs(obs_prop - p_hat))  # Mean Absolute Error
    return {
        "loglik": ll,
        "loglik_null": ll_null,
        "AIC": AIC,
        "BIC": BIC,
        "chi2": chi2,
        "reduced_chi2": reduced_chi2,
        "df": df,
        "pseudoR2_mcf": pseudoR2_mcf,
        "deviance_R2": deviance_R2,
        "deviance": dev_model,
        "reduced_deviance": reduced_deviance,
        "rmse": rmse,
        "mae": mae,
    }


def weighted_R2(y_obs, y_pred, weights=None):
    """
    重み付き決定係数（R²）を計算する関数
    
    Parameters:
    -----------
    y_obs : array-like
        観測値（比率データ）
    y_pred : array-like
        予測値（フィッティング値）
    weights : array-like, optional
        各データ点の重み（試行数nなどを想定）。Noneの場合は重みなし
        
    Returns:
    --------
    float
        重み付きR²値（0-1の範囲、1に近いほど良好な適合）
    """
    y_obs = np.asarray(y_obs)
    y_pred = np.asarray(y_pred)
    if weights is None:
        # 重みなしの場合：通常のR²計算
        ss_res = np.sum((y_obs - y_pred) ** 2)  # 残差平方和
        ss_tot = np.sum((y_obs - np.mean(y_obs)) ** 2)  # 総平方和
    else:
        # 重み付きの場合：試行数nなどで重み付け
        w = np.asarray(weights)
        mean_w = np.sum(w * y_obs) / np.sum(w)  # 重み付き平均
        ss_res = np.sum(w * (y_obs - y_pred) ** 2)  # 重み付き残差平方和
        ss_tot = np.sum(w * (y_obs - mean_w) ** 2)  # 重み付き総平方和
    return 1 - ss_res / ss_tot if ss_tot > 0 else np.nan

# =============================================================================
# グローバル変数（パラメータ初期値は各被験者のデータに基づいて自動設定）
# =============================================================================
params_init = None  # 初期値はfit_gaussian内で各被験者のデータに基づいて自動計算
param_bounds = None  # 境界値も同様に自動設定

# =============================================================================
# メインのフィッティング関数
# =============================================================================

def fit_gaussian(x_values, observations, k_counts=None, n_trials=None):
    """
    ガウシアン関数でデータをフィッティングし、各種指標を計算する
    
    Parameters:
    -----------
    x_values : array-like
        SOA値（刺激間隔）の配列
    observations : array-like
        観測された同時性判定の比率（0-1の範囲）
    k_counts : array-like, optional
        各SOAでの成功数（同時性と判定した回数）
    n_trials : array-like, optional
        各SOAでの試行数（総回答数）
        
    Returns:
    --------
    dict
        以下のキーを含む辞書：
        - popt: 変換後のパラメータ [A, mu, sigma, B]
        - popt_raw: 生のパラメータ空間での値（デバッグ用）
        - Gfit: 全グリッドでのフィッティング値
        - begin, end: 50%閾値の両端（Window size計算用）
        - pss: Point of Subjective Simultaneity（ピーク位置）
        - prob: ピークの縦軸の値
        - reduced_chi_squared: 正規化されたカイ二乗値
        - r_squared: 決定係数（R²）または擬似R²
        - AIC, BIC: モデル選択指標（k_counts, n_trialsが提供された場合）
        - その他の適合度指標
    """
    # データの前処理：NaN値を除外
    obs = np.asarray(observations, dtype=float)
    mask = ~np.isnan(obs)  # NaNでないデータのマスク
    x_fit = x_values[mask]
    y_fit = obs[mask]
    if x_fit.size < 3:
        raise ValueError("有効なデータ点が不足しています。")

    # =====================================================================
    # パラメータ初期値と境界値の自動設定
    # 各被験者のデータに基づいて適切な初期値を計算
    # =====================================================================
    if params_init is None:
        # handle missing data robustly
        if x_fit.size == 0 or np.all(np.isnan(y_fit)):
            # defaults in raw space: A_raw=0 (sigmoid->0.5), mu=-500, log_sigma=log(150), B_raw=logit(0.01)
            local_params_init = np.array([0.0, -500.0, np.log(150.0), logit(0.01)])
            local_param_bounds = ((-10.0, -np.inf, np.log(1e-3), -10.0), (10.0, np.inf, np.log(1e4), 10.0))
        else:
            # baseline B0: robust low percentile
            B0 = float(np.nanpercentile(y_fit, 5))
            B0 = np.clip(B0, 1e-6, 0.99)

            # amplitude A0: peak - baseline, keep within (small, 1-B0)
            A0 = float(np.nanmax(y_fit) - B0)
            A0 = np.clip(A0, 1e-6, max(1.0 - B0 - 1e-6, 1e-6))

            # mu0: x at max observed proportion (fallback to weighted mean)
            try:
                mu0 = float(x_fit[np.nanargmax(y_fit)])
            except Exception:
                mu0 = float(np.sum(x_fit * np.nan_to_num(y_fit)) / np.sum(np.nan_to_num(y_fit) + 1e-12))

            # sigma0: heuristic - cover observed x-range (6σ rule), with floor to avoid tiny sigma
            span = float(np.nanmax(x_fit) - np.nanmin(x_fit))
            sigma0 = max(span / 6.0, 20.0)   # 20 ms floor

            # transform to raw parameterization
            B0_clipped = np.clip(B0, 1e-6, 1.0 - 1e-6)
            B_raw0 = logit(B0_clipped)
            frac = A0 / (1.0 - B0_clipped)
            frac = np.clip(frac, 1e-6, 1.0 - 1e-6)
            A_raw0 = logit(frac)
            log_sigma0 = np.log(max(sigma0, 1e-3))

            local_params_init = np.array([A_raw0, mu0, log_sigma0, B_raw0])

            # bounds in raw space (wide but finite)
            lower = (-10.0, float(np.nanmin(x_fit) - 1000.0), np.log(1e-3), -10.0)
            upper = (10.0, float(np.nanmax(x_fit) + 1000.0), np.log(1e4), 10.0)
            local_param_bounds = (lower, upper)
    else:
        local_params_init = params_init
        local_param_bounds = param_bounds

    # =====================================================================
    # フィッティング実行
    # =====================================================================
    try:
        # 境界値ありでフィッティング試行
        popt, _ = curve_fit(fitfunc, x_fit, y_fit, p0=local_params_init.copy(), 
                          bounds=local_param_bounds, maxfev=5000)
    except Exception as e:
        # 境界値で失敗した場合、境界値なしで再試行
        try:
            popt, _ = curve_fit(fitfunc, x_fit, y_fit, p0=local_params_init.copy(), 
                              maxfev=10000)
        except Exception as e2:
            raise RuntimeError(f"curve_fit failed: {e}; fallback also failed: {e2}")

    # =====================================================================
    # パラメータの変換（生のパラメータ空間から解釈可能な値へ）
    # =====================================================================
    A_raw, mu_hat, log_sigma_hat, B_raw = popt
    B_hat = expit(B_raw)
    A_hat = (1.0 - B_hat) * expit(A_raw)
    sigma_hat = np.exp(log_sigma_hat)
    popt_trans = np.array([A_hat, mu_hat, sigma_hat, B_hat])

    # =====================================================================
    # フィッティング値の計算
    # =====================================================================
    Gfit = fitfunc(xgv, *popt)  # 全グリッドでのフィッティング値（グラフ描画用）
    y_fitted = fitfunc(x_fit, *popt)  # 観測されたx値での予測値（適合度計算用）

    # =====================================================================
    # 適合度指標の計算
    # =====================================================================
    metrics = {}
    if (k_counts is not None) and (n_trials is not None):
        # 成功数kと試行数nが提供されている場合：二項モデルに基づく正確な指標を計算
        k_arr = np.asarray(k_counts, dtype=float)[mask]
        n_arr = np.asarray(n_trials, dtype=float)[mask]
        metrics = metrics_binomial(k_arr, n_arr, x_fit, popt, fitfunc)
        # 二項モデルでは、reduced devianceがより安定した指標
        reduced_metric = metrics.get("reduced_deviance", metrics.get("reduced_chi2", np.nan))
        r_squared = metrics.get("deviance_R2", np.nan)  # デビアンスベースのR²
        reduced_chi_squared = reduced_metric
    else:
        # 比率データのみの場合：重み付きR²を使用（試行数が不明な場合は通常のR²）
        r_squared = weighted_R2(y_fit, y_fitted)
        reduced_chi_squared = np.nan  # 正確なreduced χ²は試行数が必要
        # その他の指標はNaNとして記録
        metrics = {
            "AIC": np.nan, 
            "BIC": np.nan, 
            "chi2": np.nan, 
            "reduced_chi2": reduced_chi_squared,
            "pseudoR2_mcf": np.nan, 
            "deviance_R2": r_squared, 
            "rmse": np.sqrt(np.mean((y_fit - y_fitted) ** 2))
        }

    # =====================================================================
    # PSS（主観的同時点）とWindow size（50%閾値）の計算
    # =====================================================================
    above = np.where(Gfit >= 0.5)[0]
    if above.size > 0:
        begin = xgv[above[0]]
        end = xgv[above[-1]]
    else:
        begin = end = np.nan
    max_index = np.argmax(Gfit)
    pss = xgv[max_index]
    prob = Gfit[max_index]
    prob_clipped = float(np.clip(prob, 0.0, 1.0))

    # =====================================================================
    # 結果のまとめ
    # =====================================================================
    out = {
        "popt_raw": popt,            # 生のパラメータ空間での値（デバッグ用）
        "popt": popt_trans,          # 変換後の解釈可能なパラメータ [A, mu, sigma, B]
        "Gfit": Gfit,                # 全グリッドでのフィッティング値
        "begin": begin,              # 50%閾値の左端（Window size計算用）
        "end": end,                  # 50%閾値の右端（Window size計算用）
        "pss": pss,                  # Point of Subjective Simultaneity（ピーク位置）
        "max_index": max_index,      # ピークのインデックス
        "prob": prob_clipped,        # ピークの縦軸の値（0-1にクリッピング）
        "reduced_chi_squared": reduced_chi_squared,  # 正規化されたカイ二乗値
        "r_squared": r_squared,      # 決定係数または擬似R²
    }
    # その他の適合度指標（AIC/BICなど）を追加
    out.update({k: metrics.get(k, np.nan) for k in 
                ["AIC", "BIC", "chi2", "pseudoR2_mcf", "deviance_R2", 
                 "rmse", "mae", "deviance", "reduced_deviance"]})
    return out

# =============================================================================
# 各被験者のデータ処理とフィッティング
# =============================================================================

individual_label_used = False  # グラフのラベル表示制御用
results_list = []  # 被験者ごとの結果を保存するリスト

for path, df in zip(file_paths, dfs):
    # =====================================================================
    # 各SOAごとの成功数kと試行数nを計算
    # これにより、正確な二項モデルに基づく適合度指標を計算可能
    # =====================================================================
    k_list = []  # 各SOAでの成功数（同時性と判定した回数）のリスト
    n_list = []  # 各SOAでの試行数（総回答数）のリスト
    
    # 応答データが格納されている列を取得（デフォルトは列5）
    resp_col = df.columns[5]
    
    for soa in analyset:
        # 該当するSOAのデータを抽出
        f1 = df[df["SOA"] == soa]
        # 成功数を計算（0/1コード化された回答の合計）
        successes = int(np.nansum(f1[resp_col])) if len(f1) > 0 else 0
        # 試行数（データ行数）
        trials = int(len(f1))
        k_list.append(successes)
        n_list.append(trials)

    # =====================================================================
    # データの準備
    # =====================================================================
    x = analyset
    # 成功率の計算（k/n）
    observations = np.asarray([(k / n) if n > 0 else np.nan 
                               for k, n in zip(k_list, n_list)], dtype=float)
    k_array = np.asarray(k_list, dtype=int)
    n_array = np.asarray(n_list, dtype=int)
    
    filename = Path(path).name
    subject_id = Path(path).stem  # 拡張子を除いたファイル名を被験者IDとして使用
    print(f"observations ({filename}): ", observations)

    try:
        result = fit_gaussian(x, observations, k_counts=k_array, n_trials=n_array)
    except ValueError as exc:
        print(f"{filename}: {exc}")
        continue

    # =====================================================================
    # 結果の表示と保存
    # =====================================================================
    print("parameter: ", result["popt"])
    print("left: ", result["begin"])
    print("right: ", result["end"])
    print("50% point: ", window_size if not np.isnan(window_size) else "N/A")
    print("PSS: ", result["pss"])
    print("Prob (peak): ", result["prob"])
    # explicit outputs for both reduced deviance and Pearson chi-square (if available)
    rd = result.get("reduced_deviance", np.nan)
    rc = result.get("reduced_chi2", np.nan)
    print("Reduced deviance: ", rd)
    print("Reduced Pearson χ²: ", rc)
    # simple comparison note (relative difference)
    try:
        if (not np.isnan(rd)) and (not np.isnan(rc)):
            rel_diff = abs(rd - rc) / max(1e-12, max(abs(rd), abs(rc)))
            if rel_diff > 0.2:
                print(f"Note: reduced_deviance and reduced_chi2 differ (rel diff={rel_diff:.2f})")
    except Exception:
        pass

    # append results (include both deviance and chi2 explicitly)
    results_list.append({
        "Subject": subject_id,
        "PSS": round(result["pss"], 1) if not np.isnan(result["pss"]) else np.nan,
        "Window_size": round(window_size, 1) if not np.isnan(window_size) else np.nan,
        "Prob": round(result["prob"], 1) if not np.isnan(result["prob"]) else np.nan,
        "AIC": round(result.get("AIC", np.nan), 2) if result.get("AIC", None) is not None else np.nan,
        "BIC": round(result.get("BIC", np.nan), 2) if result.get("BIC", None) is not None else np.nan,
        "Reduced_deviance": round(result.get("reduced_deviance", np.nan), 3) if not np.isnan(result.get("reduced_deviance", np.nan)) else np.nan,
        "Reduced_chi2": round(result.get("reduced_chi2", np.nan), 3) if not np.isnan(result.get("reduced_chi2", np.nan)) else np.nan,
    })

    # =====================================================================
    # グラフへの個人データのプロット
    # =====================================================================
    label = "individual" if not individual_label_used else None  # 最初の1回だけラベルを表示
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

# =============================================================================
# 全被験者のデータを集約して解析
# =============================================================================

# 全CSVファイルのデータを結合
df_all = pd.concat(dfs, ignore_index=True)

# 集約データ用の成功数kと試行数nを計算
aggregate_k = []
aggregate_n = []
resp_col = df_all.columns[5]  # 応答データの列

for soa in analyset:
    # 全被験者の該当SOAのデータを抽出
    f = df_all[df_all["SOA"] == soa]
    # 成功数（全被験者の合計）
    successes = int(np.nansum(f[resp_col])) if len(f) > 0 else 0
    # 試行数（全被験者の合計）
    trials = int(len(f))
    aggregate_k.append(successes)
    aggregate_n.append(trials)

aggregate_k = np.asarray(aggregate_k, dtype=int)
aggregate_n = np.asarray(aggregate_n, dtype=int)
# 集約データの成功率を計算
aggregate_observations = np.asarray([(k / n) if n > 0 else np.nan 
                                     for k, n in zip(aggregate_k, aggregate_n)], dtype=float)

print("observations (aggregate): ", aggregate_observations)

aggregate_result = None
try:
    aggregate_result = fit_gaussian(analyset, aggregate_observations, k_counts=aggregate_k, n_trials=aggregate_n)
except ValueError as exc:
    print(f"aggregate: {exc}")

if aggregate_result is not None:
    # =====================================================================
    # 集約データの結果を表示と保存
    # =====================================================================
    print("parameter: ", aggregate_result["popt"])
    print("left: ", aggregate_result["begin"])
    print("right: ", aggregate_result["end"])
    window_size_agg = np.nan
    if not np.isnan(aggregate_result["begin"]) and not np.isnan(aggregate_result["end"]):
        window_size_agg = aggregate_result["end"] - aggregate_result["begin"]
        print("50% point: ", window_size_agg)
    print("PSS: ", aggregate_result["pss"])
    print("Prob (peak): ", aggregate_result["prob"])
    rd_ag = aggregate_result.get("reduced_deviance", np.nan)
    rc_ag = aggregate_result.get("reduced_chi2", np.nan)
    print("Reduced deviance (aggregate): ", rd_ag)
    print("Reduced Pearson χ² (aggregate): ", rc_ag)
    try:
        if (not np.isnan(rd_ag)) and (not np.isnan(rc_ag)):
            rel_diff_ag = abs(rd_ag - rc_ag) / max(1e-12, max(abs(rd_ag), abs(rc_ag)))
            if rel_diff_ag > 0.2:
                print(f"Note (aggregate): reduced_deviance and reduced_chi2 differ (rel diff={rel_diff_ag:.2f})")
    except Exception:
        pass

    # append aggregate result (include both deviance and chi2 explicitly)
    results_list.append({
        "Subject": "aggregate",
        "PSS": round(aggregate_result["pss"], 1) if not np.isnan(aggregate_result["pss"]) else np.nan,
        "Window_size": round(window_size_agg, 1) if not np.isnan(window_size_agg) else np.nan,
        "Prob": round(aggregate_result["prob"], 1) if not np.isnan(aggregate_result["prob"]) else np.nan,
        "AIC": round(aggregate_result.get("AIC", np.nan), 2) if aggregate_result.get("AIC", None) is not None else np.nan,
        "BIC": round(aggregate_result.get("BIC", np.nan), 2) if aggregate_result.get("BIC", None) is not None else np.nan,
        "Reduced_deviance": round(aggregate_result.get("reduced_deviance", np.nan), 3) if not np.isnan(aggregate_result.get("reduced_deviance", np.nan)) else np.nan,
        "Reduced_chi2": round(aggregate_result.get("reduced_chi2", np.nan), 3) if not np.isnan(aggregate_result.get("reduced_chi2", np.nan)) else np.nan,
    })

    # =====================================================================
    # 集約データのグラフプロット
    # =====================================================================
    # フィッティング曲線（太線で強調表示）
    plt.plot(
        xgv,
        aggregate_result["Gfit"],
        "-",
        linewidth=4.0,
        color="#1D77B4",
        label="average fitting curve",
        alpha=1.0,
    )
    # 実際のデータポイント
    plt.plot(
        analyset,
        aggregate_observations,
        ".",
        color="#DB5958",
        label="average data",
        alpha=0.9,
    )

# =============================================================================
# グラフの書式設定
# =============================================================================
plt.xlabel("SOA(ms)", fontsize=28, fontweight="bold")
plt.ylabel("Probability of simultaneity response", fontsize=25, fontweight="bold")

# y軸の目盛り設定（確率なので0-1の範囲）
plt.yticks([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])

# 軸の範囲設定
plt.xlim([-2500, 1500])
plt.ylim([0, 1.05])

# =============================================================================
# 集約データの補助的な可視化（PSSの垂直線と50%窓の塗りつぶし）
# =============================================================================
if aggregate_result is not None:
    # PSS（主観的同時点）の位置を示す垂直線
    plt.vlines(
        aggregate_result["pss"],
        0,
        aggregate_result["Gfit"][aggregate_result["max_index"]],
        color="#1D77B4",
        linestyles="dashed",
        label="average PSS",
    )
    # 50%閾値の範囲を塗りつぶし（Window sizeの可視化）
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

# =============================================================================
# 結果のCSVファイルへの保存
# =============================================================================
if results_list:
    results_df = pd.DataFrame(results_list)
    # ファイル保存ダイアログを表示して保存場所を選択
    output_path = filedialog.asksaveasfilename(
        title="Save results as CSV",
        defaultextension=".csv",
        filetypes=(("CSV files", "*.csv"), ("All files", "*")),
    )
    if output_path:
        # UTF-8 BOM付きで保存（Excelで開く際の文字化け防止）
        results_df.to_csv(output_path, index=False, encoding="utf-8-sig")
        print(f"\n結果を保存しました: {output_path}")
        print("\n保存されたデータ:")
        print(results_df.to_string(index=False))
    else:
        print("\nCSVファイルの保存がキャンセルされました。")
else:
    print("\n保存する結果がありませんでした。")
