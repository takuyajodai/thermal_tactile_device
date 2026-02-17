#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 2023

Thermal-tactile simultaneity judgment analysis using Gaussian fitting.

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

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.special import xlogy, expit, logit
import sys
sys.path.append(str(Path(__file__).parent))
from window_validation import validate_window_size

# Load custom style
style_path = Path(__file__).parent.parent / "utils" / "dsheep_white.mplstyle"
plt.style.use(str(style_path))

# =============================================================================
# データ読み込み
# =============================================================================

# CLI引数でCSVファイルパスが指定されている場合はそれを使用、なければファイルダイアログ
if len(sys.argv) >= 2:
    file_paths = sys.argv[1:]
else:
    from tkinter import filedialog
    file_paths = filedialog.askopenfilenames(
        title="Select spatial cold CSV files",
        filetypes=(("CSV files", "*.csv"), ("All files", "*")),
    )

if not file_paths:
    raise SystemExit("ファイルが選択されませんでした。")

# 選択された全てのCSVファイルを読み込む（エンコーディング自動検出）
dfs = []
for file in file_paths:
    try:
        dfs.append(pd.read_csv(file, header=0, encoding="utf-8-sig"))
    except UnicodeDecodeError:
        dfs.append(pd.read_csv(file, header=0, encoding="cp932"))

# =============================================================================
# 解析パラメータの設定
# =============================================================================

# 解析対象のSOA値をデフォルトで設定し、データから自動検出も行う
_DEFAULT_ANALYSET = np.array([-2000, -1500, -1200, -1000, -850, -700, -550, -400, -200, 100, 600])

# データ内の実際のSOA値を取得（全CSVファイルの和集合）
_all_soas = set()
for df in dfs:
    _all_soas.update(df["SOA"].dropna().unique())
_detected_soas = np.array(sorted(_all_soas))

# デフォルトのSOA値とデータのSOA値が一致するか確認
if set(_DEFAULT_ANALYSET).issubset(set(_detected_soas)):
    analyset = _DEFAULT_ANALYSET
else:
    analyset = _detected_soas
    print(f"[INFO] SOA値をデータから自動検出しました: {analyset}")
    if not np.array_equal(_detected_soas, _DEFAULT_ANALYSET):
        print(f"[INFO] デフォルト値 {_DEFAULT_ANALYSET} とは異なります")

# フィッティング曲線の描画用グリッド（詳細な曲線を描くため）
_soa_min = analyset.min()
_soa_max = analyset.max()
_soa_margin = max(500, int((_soa_max - _soa_min) * 0.2))
N = int(_soa_max - _soa_min + 2 * _soa_margin)
xgv = np.arange(0.0, N) + _soa_min - _soa_margin

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

def _safe_divide(numerator, denominator, default=np.nan):
    """安全な除算：NaN/infチェック付き"""
    if np.isnan(denominator) or np.isinf(denominator) or denominator == 0:
        return default
    result = numerator / denominator
    return default if (np.isnan(result) or np.isinf(result)) else result

def _safe_value(value, default=np.nan):
    """NaN/infチェック付きの値返却"""
    return default if (np.isnan(value) or np.isinf(value)) else value

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
    # 有効なデータポイントのマスク（統計計算で使用）
    # =====================================================================
    p_param = len(popt)  # パラメータ数
    # 有効なデータポイントのみをカウント（n > 0 かつ NaNでない、p_hatも有効）
    valid_for_stats = (n > 0) & ~np.isnan(k) & ~np.isnan(n) & ~np.isnan(p_hat)
    N = np.sum(valid_for_stats)  # 有効なデータ点数
    
    # =====================================================================
    # 対数尤度の計算（二項分布に基づく）
    # =====================================================================
    # 有効なデータポイントがない場合は、全ての指標をNaNとして返す
    if N == 0:
        return {
            "loglik": np.nan,
            "loglik_null": np.nan,
            "AIC": np.nan,
            "BIC": np.nan,
            "chi2": np.nan,
            "reduced_chi2": np.nan,
            "df": np.nan,
            "pseudoR2_mcf": np.nan,
            "deviance_R2": np.nan,
            "deviance": np.nan,
            "reduced_deviance": np.nan,
            "rmse": np.nan,
            "mae": np.nan,
        }
    
    # フィッティングモデルの対数尤度
    ll = np.sum(xlogy(k[valid_for_stats], p_hat[valid_for_stats]) + 
                xlogy(n[valid_for_stats] - k[valid_for_stats], 1 - p_hat[valid_for_stats]))
    ll = _safe_value(ll)
    
    # ヌルモデル（定数確率モデル）の対数尤度
    total_n = np.sum(n[valid_for_stats])
    if total_n > 0:
        p0 = np.clip(np.sum(k[valid_for_stats]) / total_n, 1e-12, 1 - 1e-12)
        ll_null = np.sum(xlogy(k[valid_for_stats], p0) + 
                        xlogy(n[valid_for_stats] - k[valid_for_stats], 1 - p0))
        ll_null = _safe_value(ll_null)
    else:
        ll_null = np.nan
    
    # モデル選択指標（AIC/BIC）
    AIC = _safe_value(2 * p_param - 2 * ll) if not np.isnan(ll) else np.nan
    BIC = _safe_value(p_param * np.log(N) - 2 * ll) if (N > 0 and not np.isnan(ll)) else np.nan
    
    # Pearsonカイ二乗統計量
    if N == 0:
        chi2 = reduced_chi2 = df = np.nan
    else:
        k_valid = k[valid_for_stats].astype(float)
        n_valid = n[valid_for_stats].astype(float)
        p_hat_clipped = np.clip(p_hat[valid_for_stats], 1e-6, 1 - 1e-6)
        
        denom = n_valid * p_hat_clipped * (1 - p_hat_clipped)
        denom = np.maximum(denom, np.maximum(1e-8, n_valid * 1e-8))
        
        if np.any(np.isnan(denom)) or np.any(np.isinf(denom)) or np.any(denom <= 0):
            chi2 = np.nan
        else:
            numerator = (k_valid - n_valid * p_hat_clipped) ** 2
            if np.any(np.isnan(numerator)) or np.any(np.isinf(numerator)):
                chi2 = np.nan
            else:
                ratio = numerator / denom
                chi2 = _safe_value(np.sum(ratio)) if not (np.any(np.isnan(ratio)) or np.any(np.isinf(ratio))) else np.nan
        
        df = N - p_param
        reduced_chi2 = _safe_divide(chi2, df) if (df > 0 and not np.isnan(chi2)) else np.nan
    
    # 擬似R²（McFadden's pseudo R²）
    pseudoR2_mcf = _safe_value(1 - _safe_divide(ll, ll_null, default=0))
    
    # デビアンスベースのR²
    p_sat = np.full_like(k, np.nan)
    p_sat[valid_for_stats] = np.clip(k[valid_for_stats] / n[valid_for_stats], 1e-12, 1 - 1e-12)
    ll_sat = np.sum(xlogy(k[valid_for_stats], p_sat[valid_for_stats]) + 
                   xlogy(n[valid_for_stats] - k[valid_for_stats], 1 - p_sat[valid_for_stats]))
    ll_sat = _safe_value(ll_sat)
    
    dev_model = _safe_value(-2 * (ll - ll_sat)) if not (np.isnan(ll) or np.isnan(ll_sat)) else np.nan
    dev_null = _safe_value(-2 * (ll_null - ll_sat)) if not (np.isnan(ll_null) or np.isnan(ll_sat)) else np.nan
    deviance_R2 = _safe_value(1 - _safe_divide(dev_model, dev_null, default=0))
    
    df_dev = N - p_param if N > 0 else np.nan
    reduced_deviance = _safe_divide(dev_model, df_dev) if (not np.isnan(df_dev) and df_dev > 0) else np.nan
    
    # 残差に関する指標（RMSE、MAE）
    if N > 0:
        obs_prop_valid = k[valid_for_stats] / n[valid_for_stats]
        p_hat_valid = p_hat[valid_for_stats]
        if not (np.any(np.isnan(obs_prop_valid)) or np.any(np.isinf(obs_prop_valid)) or 
                np.any(np.isnan(p_hat_valid)) or np.any(np.isinf(p_hat_valid))):
            rmse = _safe_value(np.sqrt(np.mean((obs_prop_valid - p_hat_valid) ** 2)))
            mae = _safe_value(np.mean(np.abs(obs_prop_valid - p_hat_valid)))
        else:
            rmse = mae = np.nan
    else:
        rmse = mae = np.nan
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
                ["AIC", "BIC", "chi2", "reduced_chi2", "pseudoR2_mcf", "deviance_R2", 
                 "rmse", "mae", "deviance", "reduced_deviance"]})
    return out

# =============================================================================
# 各被験者のデータ処理とフィッティング
# =============================================================================

individual_label_used = False  # グラフのラベル表示制御用
results_list = []  # 被験者ごとの結果を保存するリスト
detailed_data_list = []  # 被験者ごとの詳細データを保存するリスト（各SOAでの観測値、予測値など）

# =============================================================================
# 第1パス：全被験者のフィッティングを実行し、結果を一時的に保存
# Window size validationのために全被験者のwindow sizeを収集する必要がある
# =============================================================================
temp_results = []  # 一時的な結果保存用

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
    window_size = np.nan
    if not np.isnan(result["begin"]) and not np.isnan(result["end"]):
        window_size = result["end"] - result["begin"]
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

    # =====================================================================
    # フィッティングパラメータの取得
    # =====================================================================
    popt_trans = result.get("popt", [np.nan, np.nan, np.nan, np.nan])
    A_param = popt_trans[0] if len(popt_trans) > 0 else np.nan
    mu_param = popt_trans[1] if len(popt_trans) > 1 else np.nan
    sigma_param = popt_trans[2] if len(popt_trans) > 2 else np.nan
    B_param = popt_trans[3] if len(popt_trans) > 3 else np.nan  # ベースラインパラメータ（理論的妥当性評価に重要）
    
    # =====================================================================
    # 極端なSOA値での観測値と予測値を計算
    # =====================================================================
    # 極端なSOA値のインデックスを取得（最小値と最大値）
    extreme_indices = [0, len(analyset) - 1]  # 最初と最後のSOA値
    extreme_soa_values = [analyset[i] for i in extreme_indices]
    extreme_obs_values = [observations[i] if i < len(observations) else np.nan for i in extreme_indices]
    # 極端なSOA値での予測値を計算
    extreme_pred_values = []
    for soa_val in extreme_soa_values:
        pred_val = fitfunc(soa_val, *result.get("popt_raw", [np.nan, np.nan, np.nan, np.nan]))
        extreme_pred_values.append(float(pred_val) if not (np.isnan(pred_val) or np.isinf(pred_val)) else np.nan)
    
    # 極端なSOA値での平均残差（理論的妥当性評価用）
    extreme_residual = np.nan
    if len(extreme_obs_values) > 0 and len(extreme_pred_values) > 0:
        valid_mask = [not (np.isnan(o) or np.isnan(p)) for o, p in zip(extreme_obs_values, extreme_pred_values)]
        if any(valid_mask):
            valid_obs = [o for o, v in zip(extreme_obs_values, valid_mask) if v]
            valid_pred = [p for p, v in zip(extreme_pred_values, valid_mask) if v]
            extreme_residual = float(np.mean(np.abs(np.array(valid_obs) - np.array(valid_pred))))
    
    # =====================================================================
    # 各SOAでの予測値を計算（詳細データ用）
    # =====================================================================
    predicted_values = []
    for soa_val in analyset:
        pred_val = fitfunc(soa_val, *result.get("popt_raw", [np.nan, np.nan, np.nan, np.nan]))
        predicted_values.append(float(pred_val) if not (np.isnan(pred_val) or np.isinf(pred_val)) else np.nan)
    
    # =====================================================================
    # 詳細データをリストに追加（各SOAごとのデータ）
    # =====================================================================
    for i, soa_val in enumerate(analyset):
        detailed_data_list.append({
            "Subject": subject_id,
            "SOA": soa_val,
            "Observed_prob": round(observations[i], 4) if i < len(observations) and not np.isnan(observations[i]) else np.nan,
            "Predicted_prob": round(predicted_values[i], 4) if i < len(predicted_values) and not np.isnan(predicted_values[i]) else np.nan,
            "Success_count": int(k_array[i]) if i < len(k_array) else np.nan,
            "Trial_count": int(n_array[i]) if i < len(n_array) else np.nan,
            "Residual": round(abs(observations[i] - predicted_values[i]), 4) if (i < len(observations) and i < len(predicted_values) and 
                                                                                  not np.isnan(observations[i]) and not np.isnan(predicted_values[i])) else np.nan,
        })
    
    # =====================================================================
    # 一時的な結果を保存（Window size validationのため）
    # =====================================================================
    temp_results.append({
        "Subject": subject_id,
        "result": result,
        "window_size": window_size,
        "A_param": A_param,
        "mu_param": mu_param,
        "sigma_param": sigma_param,
        "B_param": B_param,
        "extreme_residual": extreme_residual,
        "predicted_values": predicted_values,
        "observations": observations,
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
# 第2パス：Window size validationを実行し、結果をresults_listに追加
# =============================================================================
# 全被験者のwindow sizeを収集
all_windows = [tr["window_size"] for tr in temp_results if not np.isnan(tr["window_size"])]

# 各被験者に対してvalidationを実行
for temp_result in temp_results:
    subject_id = temp_result["Subject"]
    result = temp_result["result"]
    window_size = temp_result["window_size"]
    A_param = temp_result["A_param"]
    mu_param = temp_result["mu_param"]
    sigma_param = temp_result["sigma_param"]
    B_param = temp_result["B_param"]
    extreme_residual = temp_result["extreme_residual"]
    predicted_values = temp_result["predicted_values"]
    observations = temp_result["observations"]
    
    # Window size validationを実行
    validation_result = {}
    if not np.isnan(window_size) and len(all_windows) >= 3:
        try:
            # xgvとGfitを使用してflatness計算用のデータを準備
            x_fit_for_validation = analyset
            y_fit_for_validation = np.array([fitfunc(x, *result.get("popt_raw", [np.nan, np.nan, np.nan, np.nan])) 
                                            for x in analyset])
            
            validation_result = validate_window_size(
                window_size=window_size,
                prob=result["prob"],
                B=B_param,
                sigma=sigma_param,
                mu=mu_param,
                all_windows=all_windows,
                fitfunc=fitfunc,
                popt_raw=result.get("popt_raw", None),
                x_values=x_fit_for_validation,
                y_values=y_fit_for_validation
            )
        except Exception as e:
            print(f"Warning: Window validation failed for {subject_id}: {e}")
            validation_result = {}
    else:
        validation_result = {}
    
    # =====================================================================
    # サマリー結果をリストに追加（validation結果を含む）
    # =====================================================================
    result_dict = {
        "Subject": subject_id,
        "PSS": round(result["pss"], 1) if not np.isnan(result["pss"]) else np.nan,
        "Window_size": round(window_size, 1) if not np.isnan(window_size) else np.nan,
        "Prob": round(result["prob"], 2) if not np.isnan(result["prob"]) else np.nan,
        "A_param": round(A_param, 4) if not np.isnan(A_param) else np.nan,
        "mu_param": round(mu_param, 1) if not np.isnan(mu_param) else np.nan,
        "sigma_param": round(sigma_param, 1) if not np.isnan(sigma_param) else np.nan,
        "B_param": round(B_param, 4) if not np.isnan(B_param) else np.nan,
        "AIC": round(result.get("AIC", np.nan), 2) if result.get("AIC", None) is not None else np.nan,
        "BIC": round(result.get("BIC", np.nan), 2) if result.get("BIC", None) is not None else np.nan,
        "Reduced_deviance": round(result.get("reduced_deviance", np.nan), 3) if not np.isnan(result.get("reduced_deviance", np.nan)) else np.nan,
        "Reduced_chi2": round(result.get("reduced_chi2", np.nan), 3) if not np.isnan(result.get("reduced_chi2", np.nan)) else np.nan,
        "Extreme_residual": round(extreme_residual, 4) if not np.isnan(extreme_residual) else np.nan,
    }
    
    # Validation結果を追加
    if validation_result:
        result_dict["PBR"] = round(validation_result.get("pbr", np.nan), 4) if not np.isnan(validation_result.get("pbr", np.nan)) else np.nan
        result_dict["Adjusted_window_size"] = round(validation_result.get("adjusted_window_size", np.nan), 1) if not np.isnan(validation_result.get("adjusted_window_size", np.nan)) else np.nan
        result_dict["Theoretical_width"] = round(validation_result.get("theoretical_width", np.nan), 1) if not np.isnan(validation_result.get("theoretical_width", np.nan)) else np.nan
        result_dict["Z_score_window"] = round(validation_result.get("stat_z_score", np.nan), 3) if not np.isnan(validation_result.get("stat_z_score", np.nan)) else np.nan
        result_dict["IQR_outlier"] = validation_result.get("stat_iqr_outlier", False)
        result_dict["Window_validity"] = validation_result.get("window_validity", "unknown")
    else:
        result_dict["PBR"] = np.nan
        result_dict["Adjusted_window_size"] = np.nan
        result_dict["Theoretical_width"] = np.nan
        result_dict["Z_score_window"] = np.nan
        result_dict["IQR_outlier"] = False
        result_dict["Window_validity"] = "insufficient_data"
    
    results_list.append(result_dict)

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

    # =====================================================================
    # 集約データのフィッティングパラメータの取得
    # =====================================================================
    popt_agg = aggregate_result.get("popt", [np.nan, np.nan, np.nan, np.nan])
    A_param_agg = popt_agg[0] if len(popt_agg) > 0 else np.nan
    mu_param_agg = popt_agg[1] if len(popt_agg) > 1 else np.nan
    sigma_param_agg = popt_agg[2] if len(popt_agg) > 2 else np.nan
    B_param_agg = popt_agg[3] if len(popt_agg) > 3 else np.nan
    
    # =====================================================================
    # 集約データの極端なSOA値での観測値と予測値を計算
    # =====================================================================
    extreme_indices_agg = [0, len(analyset) - 1]
    extreme_soa_values_agg = [analyset[i] for i in extreme_indices_agg]
    extreme_obs_values_agg = [aggregate_observations[i] if i < len(aggregate_observations) else np.nan for i in extreme_indices_agg]
    extreme_pred_values_agg = []
    for soa_val in extreme_soa_values_agg:
        pred_val = fitfunc(soa_val, *aggregate_result.get("popt_raw", [np.nan, np.nan, np.nan, np.nan]))
        extreme_pred_values_agg.append(float(pred_val) if not (np.isnan(pred_val) or np.isinf(pred_val)) else np.nan)
    
    extreme_residual_agg = np.nan
    if len(extreme_obs_values_agg) > 0 and len(extreme_pred_values_agg) > 0:
        valid_mask_agg = [not (np.isnan(o) or np.isnan(p)) for o, p in zip(extreme_obs_values_agg, extreme_pred_values_agg)]
        if any(valid_mask_agg):
            valid_obs_agg = [o for o, v in zip(extreme_obs_values_agg, valid_mask_agg) if v]
            valid_pred_agg = [p for p, v in zip(extreme_pred_values_agg, valid_mask_agg) if v]
            extreme_residual_agg = float(np.mean(np.abs(np.array(valid_obs_agg) - np.array(valid_pred_agg))))
    
    # =====================================================================
    # 集約データの詳細データをリストに追加
    # =====================================================================
    predicted_values_agg = []
    for soa_val in analyset:
        pred_val = fitfunc(soa_val, *aggregate_result.get("popt_raw", [np.nan, np.nan, np.nan, np.nan]))
        predicted_values_agg.append(float(pred_val) if not (np.isnan(pred_val) or np.isinf(pred_val)) else np.nan)
    
    for i, soa_val in enumerate(analyset):
        detailed_data_list.append({
            "Subject": "aggregate",
            "SOA": soa_val,
            "Observed_prob": round(aggregate_observations[i], 4) if i < len(aggregate_observations) and not np.isnan(aggregate_observations[i]) else np.nan,
            "Predicted_prob": round(predicted_values_agg[i], 4) if i < len(predicted_values_agg) and not np.isnan(predicted_values_agg[i]) else np.nan,
            "Success_count": int(aggregate_k[i]) if i < len(aggregate_k) else np.nan,
            "Trial_count": int(aggregate_n[i]) if i < len(aggregate_n) else np.nan,
            "Residual": round(abs(aggregate_observations[i] - predicted_values_agg[i]), 4) if (i < len(aggregate_observations) and i < len(predicted_values_agg) and 
                                                                                              not np.isnan(aggregate_observations[i]) and not np.isnan(predicted_values_agg[i])) else np.nan,
        })
    
    # =====================================================================
    # 集約データのWindow size validationを実行
    # =====================================================================
    validation_result_agg = {}
    if not np.isnan(window_size_agg) and len(all_windows) >= 3:
        try:
            x_fit_for_validation_agg = analyset
            y_fit_for_validation_agg = np.array([fitfunc(x, *aggregate_result.get("popt_raw", [np.nan, np.nan, np.nan, np.nan])) 
                                                 for x in analyset])
            
            validation_result_agg = validate_window_size(
                window_size=window_size_agg,
                prob=aggregate_result["prob"],
                B=B_param_agg,
                sigma=sigma_param_agg,
                mu=mu_param_agg,
                all_windows=all_windows,  # 個別被験者のwindow sizeと比較
                fitfunc=fitfunc,
                popt_raw=aggregate_result.get("popt_raw", None),
                x_values=x_fit_for_validation_agg,
                y_values=y_fit_for_validation_agg
            )
        except Exception as e:
            print(f"Warning: Window validation failed for aggregate: {e}")
            validation_result_agg = {}
    else:
        validation_result_agg = {}
    
    # =====================================================================
    # 集約データのサマリー結果をリストに追加（validation結果を含む）
    # =====================================================================
    result_dict_agg = {
        "Subject": "aggregate",
        "PSS": round(aggregate_result["pss"], 1) if not np.isnan(aggregate_result["pss"]) else np.nan,
        "Window_size": round(window_size_agg, 1) if not np.isnan(window_size_agg) else np.nan,
        "Prob": round(aggregate_result["prob"], 2) if not np.isnan(aggregate_result["prob"]) else np.nan,
        "A_param": round(A_param_agg, 4) if not np.isnan(A_param_agg) else np.nan,
        "mu_param": round(mu_param_agg, 1) if not np.isnan(mu_param_agg) else np.nan,
        "sigma_param": round(sigma_param_agg, 1) if not np.isnan(sigma_param_agg) else np.nan,
        "B_param": round(B_param_agg, 4) if not np.isnan(B_param_agg) else np.nan,
        "AIC": round(aggregate_result.get("AIC", np.nan), 2) if aggregate_result.get("AIC", None) is not None else np.nan,
        "BIC": round(aggregate_result.get("BIC", np.nan), 2) if aggregate_result.get("BIC", None) is not None else np.nan,
        "Reduced_deviance": round(aggregate_result.get("reduced_deviance", np.nan), 3) if not np.isnan(aggregate_result.get("reduced_deviance", np.nan)) else np.nan,
        "Reduced_chi2": round(aggregate_result.get("reduced_chi2", np.nan), 3) if not np.isnan(aggregate_result.get("reduced_chi2", np.nan)) else np.nan,
        "Extreme_residual": round(extreme_residual_agg, 4) if not np.isnan(extreme_residual_agg) else np.nan,
    }
    
    # Validation結果を追加
    if validation_result_agg:
        result_dict_agg["PBR"] = round(validation_result_agg.get("pbr", np.nan), 4) if not np.isnan(validation_result_agg.get("pbr", np.nan)) else np.nan
        result_dict_agg["Adjusted_window_size"] = round(validation_result_agg.get("adjusted_window_size", np.nan), 1) if not np.isnan(validation_result_agg.get("adjusted_window_size", np.nan)) else np.nan
        result_dict_agg["Theoretical_width"] = round(validation_result_agg.get("theoretical_width", np.nan), 1) if not np.isnan(validation_result_agg.get("theoretical_width", np.nan)) else np.nan
        result_dict_agg["Z_score_window"] = round(validation_result_agg.get("stat_z_score", np.nan), 3) if not np.isnan(validation_result_agg.get("stat_z_score", np.nan)) else np.nan
        result_dict_agg["IQR_outlier"] = validation_result_agg.get("stat_iqr_outlier", False)
        result_dict_agg["Window_validity"] = validation_result_agg.get("window_validity", "unknown")
    else:
        result_dict_agg["PBR"] = np.nan
        result_dict_agg["Adjusted_window_size"] = np.nan
        result_dict_agg["Theoretical_width"] = np.nan
        result_dict_agg["Z_score_window"] = np.nan
        result_dict_agg["IQR_outlier"] = False
        result_dict_agg["Window_validity"] = "insufficient_data"
    
    results_list.append(result_dict_agg)

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

# 軸の範囲設定（データの範囲に基づいて自動調整）
plt.xlim([_soa_min - _soa_margin, _soa_max + _soa_margin])
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
    # CLI実行時は入力CSVと同じディレクトリに自動保存、GUI時はダイアログ
    if len(sys.argv) >= 2:
        _input_dir = Path(file_paths[0]).parent
        output_path = str(_input_dir / "fitting_summary.csv")
    else:
        from tkinter import filedialog as _fd_save
        output_path = _fd_save.asksaveasfilename(
            title="Save summary results as CSV",
            defaultextension=".csv",
            filetypes=(("CSV files", "*.csv"), ("All files", "*")),
        )
    if output_path:
        # UTF-8 BOM付きで保存（Excelで開く際の文字化け防止）
        results_df.to_csv(output_path, index=False, encoding="utf-8-sig")
        print(f"\nサマリー結果を保存しました: {output_path}")
        print("\n保存されたデータ:")
        print(results_df.to_string(index=False))
        
        # 詳細データも保存するか確認
        if detailed_data_list:
            # 詳細データの保存先を自動的に決定（サマリーファイル名に "_detailed" を追加）
            detailed_output_path = str(Path(output_path).with_name(
                Path(output_path).stem + "_detailed" + Path(output_path).suffix
            ))
            detailed_df = pd.DataFrame(detailed_data_list)
            detailed_df.to_csv(detailed_output_path, index=False, encoding="utf-8-sig")
            print(f"\n詳細データを保存しました: {detailed_output_path}")
            print(f"（各被験者・各SOAでの観測値、予測値、成功数、試行数、残差を含みます）")
    else:
        print("\nCSVファイルの保存がキャンセルされました。")
else:
    print("\n保存する結果がありませんでした。")
