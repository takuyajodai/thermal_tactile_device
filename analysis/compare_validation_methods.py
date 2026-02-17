#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compare three window size validation methods.

This script applies three different validation methods (simple, moderate, comprehensive)
to the same dataset and compares the results.
"""

from tkinter import filedialog
from pathlib import Path
import numpy as np
import pandas as pd
import time
import sys
sys.path.append(str(Path(__file__).parent))

from window_validation_simple import validate_window_size_simple
from window_validation_moderate import validate_window_size_moderate
from window_validation_comprehensive import validate_window_size_comprehensive

# Import fitting function from main analysis script
from Gaussian_fitting_integrate_spatial_cold import fit_gaussian, fitfunc, analyset, xgv

# =============================================================================
# Data loading (same as main script)
# =============================================================================

file_paths = filedialog.askopenfilenames(
    title="Select spatial cold CSV files",
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

# =============================================================================
# Process all subjects and collect data
# =============================================================================

temp_results = []

for path, df in zip(file_paths, dfs):
    k_list = []
    n_list = []
    resp_col = df.columns[5]
    
    for soa in analyset:
        f1 = df[df["SOA"] == soa]
        successes = int(np.nansum(f1[resp_col])) if len(f1) > 0 else 0
        trials = int(len(f1))
        k_list.append(successes)
        n_list.append(trials)
    
    x = analyset
    observations = np.asarray([(k / n) if n > 0 else np.nan 
                               for k, n in zip(k_list, n_list)], dtype=float)
    k_array = np.asarray(k_list, dtype=int)
    n_array = np.asarray(n_list, dtype=int)
    
    filename = Path(path).name
    subject_id = Path(path).stem
    
    try:
        result = fit_gaussian(x, observations, k_counts=k_array, n_trials=n_array)
    except ValueError as exc:
        print(f"{filename}: {exc}")
        continue
    
    window_size = np.nan
    if not np.isnan(result["begin"]) and not np.isnan(result["end"]):
        window_size = result["end"] - result["begin"]
    
    popt_trans = result.get("popt", [np.nan, np.nan, np.nan, np.nan])
    A_param = popt_trans[0] if len(popt_trans) > 0 else np.nan
    mu_param = popt_trans[1] if len(popt_trans) > 1 else np.nan
    sigma_param = popt_trans[2] if len(popt_trans) > 2 else np.nan
    B_param = popt_trans[3] if len(popt_trans) > 3 else np.nan
    
    # Calculate predicted values
    predicted_values = []
    for soa_val in analyset:
        pred_val = fitfunc(soa_val, *result.get("popt_raw", [np.nan, np.nan, np.nan, np.nan]))
        predicted_values.append(float(pred_val) if not (np.isnan(pred_val) or np.isinf(pred_val)) else np.nan)
    
    temp_results.append({
        "Subject": subject_id,
        "result": result,
        "window_size": window_size,
        "prob": result["prob"],
        "B_param": B_param,
        "sigma_param": sigma_param,
        "mu_param": mu_param,
        "reduced_deviance": result.get("reduced_deviance", np.nan),
        "reduced_chi2": result.get("reduced_chi2", np.nan),
        "observations": observations,
        "predicted_values": np.array(predicted_values),
    })

# Collect all window sizes
all_windows = [tr["window_size"] for tr in temp_results if not np.isnan(tr["window_size"])]

# =============================================================================
# Apply three validation methods
# =============================================================================

comparison_results = []

for temp_result in temp_results:
    subject_id = temp_result["Subject"]
    result = temp_result["result"]
    window_size = temp_result["window_size"]
    prob = temp_result["prob"]
    B_param = temp_result["B_param"]
    sigma_param = temp_result["sigma_param"]
    mu_param = temp_result["mu_param"]
    reduced_deviance = temp_result["reduced_deviance"]
    reduced_chi2 = temp_result["reduced_chi2"]
    observations = temp_result["observations"]
    predicted_values = temp_result["predicted_values"]
    
    # Prepare data for comprehensive method
    x_fit_for_validation = analyset
    y_fit_for_validation = np.array([fitfunc(x, *result.get("popt_raw", [np.nan, np.nan, np.nan, np.nan])) 
                                    for x in analyset])
    
    # Method 1: Simple
    start_time = time.time()
    simple_result = validate_window_size_simple(
        window_size=window_size,
        reduced_deviance=reduced_deviance,
        reduced_chi2=reduced_chi2,
        all_windows=all_windows
    )
    simple_time = time.time() - start_time
    
    # Method 2: Moderate
    start_time = time.time()
    moderate_result = validate_window_size_moderate(
        window_size=window_size,
        prob=prob,
        B=B_param,
        all_windows=all_windows,
        reduced_deviance=reduced_deviance,
        reduced_chi2=reduced_chi2
    )
    moderate_time = time.time() - start_time
    
    # Method 3: Comprehensive
    start_time = time.time()
    comprehensive_result = validate_window_size_comprehensive(
        window_size=window_size,
        prob=prob,
        B=B_param,
        sigma=sigma_param,
        mu=mu_param,
        all_windows=all_windows,
        reduced_deviance=reduced_deviance,
        reduced_chi2=reduced_chi2
    )
    comprehensive_time = time.time() - start_time
    
    # Store comparison results
    comparison_results.append({
        "Subject": subject_id,
        "Window_size": round(window_size, 1) if not np.isnan(window_size) else np.nan,
        "Prob": round(prob, 2) if not np.isnan(prob) else np.nan,
        "B_param": round(B_param, 4) if not np.isnan(B_param) else np.nan,
        "Reduced_deviance": round(reduced_deviance, 3) if not np.isnan(reduced_deviance) else np.nan,
        # Simple method results
        "Simple_validity": simple_result.get("window_validity", "unknown"),
        "Simple_goodness_status": simple_result.get("goodness_status", "unknown"),
        "Simple_z_score": round(simple_result.get("z_score", np.nan), 3) if not np.isnan(simple_result.get("z_score", np.nan)) else np.nan,
        "Simple_time_ms": round(simple_time * 1000, 3),
        # Moderate method results
        "Moderate_validity": moderate_result.get("window_validity", "unknown"),
        "Moderate_pbr": round(moderate_result.get("pbr", np.nan), 4) if not np.isnan(moderate_result.get("pbr", np.nan)) else np.nan,
        "Moderate_z_score": round(moderate_result.get("stat_z_score", np.nan), 3) if not np.isnan(moderate_result.get("stat_z_score", np.nan)) else np.nan,
        "Moderate_time_ms": round(moderate_time * 1000, 3),
        # Comprehensive method results
        "Comprehensive_validity": comprehensive_result.get("window_validity", "unknown"),
        "Comprehensive_goodness_status": comprehensive_result.get("goodness_status", "unknown"),
        "Comprehensive_pbr": round(comprehensive_result.get("pbr", np.nan), 4) if not np.isnan(comprehensive_result.get("pbr", np.nan)) else np.nan,
        "Comprehensive_time_ms": round(comprehensive_time * 1000, 3),
    })

# =============================================================================
# Aggregate data processing
# =============================================================================

df_all = pd.concat(dfs, ignore_index=True)
aggregate_k = []
aggregate_n = []
resp_col = df_all.columns[5]

for soa in analyset:
    f = df_all[df_all["SOA"] == soa]
    successes = int(np.nansum(f[resp_col])) if len(f) > 0 else 0
    trials = int(len(f))
    aggregate_k.append(successes)
    aggregate_n.append(trials)

aggregate_k = np.asarray(aggregate_k, dtype=int)
aggregate_n = np.asarray(aggregate_n, dtype=int)
aggregate_observations = np.asarray([(k / n) if n > 0 else np.nan 
                                     for k, n in zip(aggregate_k, aggregate_n)], dtype=float)

aggregate_result = None
try:
    aggregate_result = fit_gaussian(analyset, aggregate_observations, k_counts=aggregate_k, n_trials=aggregate_n)
except ValueError as exc:
    print(f"aggregate: {exc}")

if aggregate_result is not None:
    window_size_agg = np.nan
    if not np.isnan(aggregate_result["begin"]) and not np.isnan(aggregate_result["end"]):
        window_size_agg = aggregate_result["end"] - aggregate_result["begin"]
    
    popt_agg = aggregate_result.get("popt", [np.nan, np.nan, np.nan, np.nan])
    B_param_agg = popt_agg[3] if len(popt_agg) > 3 else np.nan
    sigma_param_agg = popt_agg[2] if len(popt_agg) > 2 else np.nan
    mu_param_agg = popt_agg[1] if len(popt_agg) > 1 else np.nan
    
    predicted_values_agg = np.array([fitfunc(x, *aggregate_result.get("popt_raw", [np.nan, np.nan, np.nan, np.nan])) 
                                     for x in analyset])
    
    # Apply three methods to aggregate data
    simple_result_agg = validate_window_size_simple(
        window_size=window_size_agg,
        reduced_deviance=aggregate_result.get("reduced_deviance", np.nan),
        reduced_chi2=aggregate_result.get("reduced_chi2", np.nan),
        all_windows=all_windows
    )
    
    moderate_result_agg = validate_window_size_moderate(
        window_size=window_size_agg,
        prob=aggregate_result["prob"],
        B=B_param_agg,
        all_windows=all_windows,
        reduced_deviance=aggregate_result.get("reduced_deviance", np.nan),
        reduced_chi2=aggregate_result.get("reduced_chi2", np.nan)
    )
    
    comprehensive_result_agg = validate_window_size_comprehensive(
        window_size=window_size_agg,
        prob=aggregate_result["prob"],
        B=B_param_agg,
        sigma=sigma_param_agg,
        mu=mu_param_agg,
        all_windows=all_windows,
        reduced_deviance=aggregate_result.get("reduced_deviance", np.nan),
        reduced_chi2=aggregate_result.get("reduced_chi2", np.nan)
    )
    
    comparison_results.append({
        "Subject": "aggregate",
        "Window_size": round(window_size_agg, 1) if not np.isnan(window_size_agg) else np.nan,
        "Prob": round(aggregate_result["prob"], 2) if not np.isnan(aggregate_result["prob"]) else np.nan,
        "B_param": round(B_param_agg, 4) if not np.isnan(B_param_agg) else np.nan,
        "Reduced_deviance": round(aggregate_result.get("reduced_deviance", np.nan), 3) if not np.isnan(aggregate_result.get("reduced_deviance", np.nan)) else np.nan,
        "Simple_validity": simple_result_agg.get("window_validity", "unknown"),
        "Simple_goodness_status": simple_result_agg.get("goodness_status", "unknown"),
        "Simple_z_score": round(simple_result_agg.get("z_score", np.nan), 3) if not np.isnan(simple_result_agg.get("z_score", np.nan)) else np.nan,
        "Simple_time_ms": 0.0,  # Not measured for aggregate
        "Moderate_validity": moderate_result_agg.get("window_validity", "unknown"),
        "Moderate_pbr": round(moderate_result_agg.get("pbr", np.nan), 4) if not np.isnan(moderate_result_agg.get("pbr", np.nan)) else np.nan,
        "Moderate_z_score": round(moderate_result_agg.get("stat_z_score", np.nan), 3) if not np.isnan(moderate_result_agg.get("stat_z_score", np.nan)) else np.nan,
        "Moderate_time_ms": 0.0,
        "Comprehensive_validity": comprehensive_result_agg.get("window_validity", "unknown"),
        "Comprehensive_goodness_status": comprehensive_result_agg.get("goodness_status", "unknown"),
        "Comprehensive_pbr": round(comprehensive_result_agg.get("pbr", np.nan), 4) if not np.isnan(comprehensive_result_agg.get("pbr", np.nan)) else np.nan,
        "Comprehensive_time_ms": 0.0,
    })

# =============================================================================
# Save comparison results
# =============================================================================

if comparison_results:
    comparison_df = pd.DataFrame(comparison_results)
    
    output_path = filedialog.asksaveasfilename(
        title="Save comparison results as CSV",
        defaultextension=".csv",
        filetypes=(("CSV files", "*.csv"), ("All files", "*")),
    )
    
    if output_path:
        comparison_df.to_csv(output_path, index=False, encoding="utf-8-sig")
        print(f"\n比較結果を保存しました: {output_path}")
        print("\n保存されたデータ:")
        print(comparison_df.to_string(index=False))
        
        # Calculate summary statistics
        print("\n=== 実行時間の比較 ===")
        print(f"Simple method平均: {comparison_df['Simple_time_ms'].mean():.3f} ms")
        print(f"Moderate method平均: {comparison_df['Moderate_time_ms'].mean():.3f} ms")
        print(f"Comprehensive method平均: {comparison_df['Comprehensive_time_ms'].mean():.3f} ms")
        
        print("\n=== 評価結果の一致率 ===")
        # Count agreements
        simple_moderate_agreement = (comparison_df['Simple_validity'] == comparison_df['Moderate_validity']).sum()
        simple_comprehensive_agreement = (comparison_df['Simple_validity'] == comparison_df['Comprehensive_validity']).sum()
        moderate_comprehensive_agreement = (comparison_df['Moderate_validity'] == comparison_df['Comprehensive_validity']).sum()
        
        total = len(comparison_df)
        print(f"Simple vs Moderate: {simple_moderate_agreement}/{total} ({100*simple_moderate_agreement/total:.1f}%)")
        print(f"Simple vs Comprehensive: {simple_comprehensive_agreement}/{total} ({100*simple_comprehensive_agreement/total:.1f}%)")
        print(f"Moderate vs Comprehensive: {moderate_comprehensive_agreement}/{total} ({100*moderate_comprehensive_agreement/total:.1f}%)")
        
        print("\n=== 各方法の評価結果分布 ===")
        print("Simple method:")
        print(comparison_df['Simple_validity'].value_counts())
        print("\nModerate method:")
        print(comparison_df['Moderate_validity'].value_counts())
        print("\nComprehensive method:")
        print(comparison_df['Comprehensive_validity'].value_counts())
    else:
        print("\nCSVファイルの保存がキャンセルされました。")
else:
    print("\n比較する結果がありませんでした。")
