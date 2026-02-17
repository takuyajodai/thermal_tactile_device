#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Window size validation module for Gaussian fitting analysis.

This module provides functions to validate window size estimates using
a multi-stage evaluation system:
1. Statistical validation (Z-score, IQR method)
2. Theoretical validity (Peak-to-Baseline Ratio, adjusted window size)
3. Combined evaluation
"""

import numpy as np
from scipy.optimize import fsolve
from typing import Dict, List, Tuple, Optional


def calculate_pbr(prob: float, B: float) -> float:
    """
    Calculate Peak-to-Baseline Ratio (PBR).
    
    Parameters:
    -----------
    prob : float
        Peak probability value (0-1)
    B : float
        Baseline parameter (0-1)
        
    Returns:
    --------
    float
        PBR value. Returns np.nan if B is 0 or invalid.
    """
    if B <= 0 or np.isnan(B) or np.isnan(prob):
        return np.nan
    return prob / B


def calculate_adjusted_window_size(window_size: float, prob: float, 
                                   threshold: float = 0.6) -> float:
    """
    Calculate adjusted window size to account for low peak values.
    
    When the peak probability is low, the window size may be underestimated.
    This function applies a correction factor.
    
    Parameters:
    -----------
    window_size : float
        Original window size (ms)
    prob : float
        Peak probability value (0-1)
    threshold : float, optional
        Threshold below which correction is applied (default: 0.6)
        
    Returns:
    --------
    float
        Adjusted window size (ms)
    """
    if np.isnan(window_size) or np.isnan(prob) or prob <= 0:
        return np.nan
    
    if prob < threshold:
        correction_factor = threshold / prob
        return window_size * correction_factor
    else:
        return window_size


def calculate_theoretical_width(sigma: float, prob: float, B: float, 
                                mu: float, fitfunc, popt_raw: np.ndarray) -> Dict[str, float]:
    """
    Calculate theoretical expected width at 0.5 threshold.
    
    Parameters:
    -----------
    sigma : float
        Standard deviation parameter
    prob : float
        Peak probability value
    B : float
        Baseline parameter
    mu : float
        Mean parameter (PSS)
    fitfunc : callable
        Fitting function
    popt_raw : np.ndarray
        Raw parameter array for fitfunc
        
    Returns:
    --------
    dict
        Dictionary containing:
        - 'fwhm': Full Width at Half Maximum (2*sqrt(2*ln(2))*sigma)
        - 'width_at_0.5': Width at 0.5 threshold (calculated numerically)
    """
    result = {}
    
    # FWHM calculation
    if not np.isnan(sigma) and sigma > 0:
        fwhm = 2 * np.sqrt(2 * np.log(2)) * sigma
        result['fwhm'] = fwhm
    else:
        result['fwhm'] = np.nan
    
    # Width at 0.5 threshold (numerical calculation)
    if not (np.isnan(prob) or np.isnan(B) or np.isnan(mu)):
        target_prob = 0.5
        
        # Find points where fitfunc(x) = 0.5
        # We need to solve: fitfunc(x, *popt_raw) = 0.5
        def equation(x):
            return fitfunc(x, *popt_raw) - target_prob
        
        # Find left and right boundaries
        # Start from mu and search outward
        search_range = 2000  # ms
        x_left = mu - search_range
        x_right = mu + search_range
        
        try:
            # Find left boundary
            left_solution = fsolve(equation, mu - sigma, xtol=1e-6)
            if len(left_solution) > 0:
                left_bound = float(left_solution[0])
            else:
                left_bound = np.nan
            
            # Find right boundary
            right_solution = fsolve(equation, mu + sigma, xtol=1e-6)
            if len(right_solution) > 0:
                right_bound = float(right_solution[0])
            else:
                right_bound = np.nan
            
            if not (np.isnan(left_bound) or np.isnan(right_bound)):
                width_at_0_5 = abs(right_bound - left_bound)
            else:
                width_at_0_5 = np.nan
        except Exception:
            width_at_0_5 = np.nan
        
        result['width_at_0.5'] = width_at_0_5
    else:
        result['width_at_0.5'] = np.nan
    
    return result


def calculate_flatness_index(x_values: np.ndarray, y_values: np.ndarray, 
                            mu: float, sigma: float) -> float:
    """
    Calculate flatness index to detect flat regions outside the peak.
    
    Parameters:
    -----------
    x_values : np.ndarray
        SOA values
    y_values : np.ndarray
        Fitted probability values
    mu : float
        Mean parameter (PSS)
    sigma : float
        Standard deviation parameter
        
    Returns:
    --------
    float
        Flatness index (0-1). Higher values indicate flatter regions.
    """
    if len(x_values) == 0 or len(y_values) == 0 or np.isnan(mu) or np.isnan(sigma):
        return np.nan
    
    # Define region outside peak (±2σ)
    peak_left = mu - 2 * sigma
    peak_right = mu + 2 * sigma
    
    # Extract values outside peak region
    outside_mask = (x_values < peak_left) | (x_values > peak_right)
    outside_y = y_values[outside_mask]
    
    if len(outside_y) < 2:
        return np.nan
    
    # Calculate coefficient of variation (CV) as flatness measure
    # Lower CV = flatter (less variation)
    mean_y = np.mean(outside_y)
    if mean_y == 0:
        return np.nan
    
    std_y = np.std(outside_y)
    cv = std_y / mean_y if mean_y > 0 else np.nan
    
    # Convert to flatness index (inverse of CV, normalized)
    # Lower CV means higher flatness
    flatness = 1.0 / (1.0 + cv) if not np.isnan(cv) else np.nan
    
    return flatness


def statistical_validation(window_size: float, all_windows: List[float]) -> Dict[str, any]:
    """
    Perform statistical validation of window size using Z-score and IQR method.
    
    Parameters:
    -----------
    window_size : float
        Window size to validate (ms)
    all_windows : List[float]
        List of all window sizes from all subjects
        
    Returns:
    --------
    dict
        Dictionary containing:
        - 'z_score': Z-score value
        - 'z_score_status': 'normal', 'warning', or 'abnormal'
        - 'iqr_outlier': Boolean indicating if IQR outlier
        - 'iqr_lower_bound': Lower bound from IQR method
        - 'iqr_upper_bound': Upper bound from IQR method
        - 'statistical_status': Combined status ('normal', 'warning', 'abnormal')
    """
    result = {}
    
    # Filter out NaN values
    valid_windows = [w for w in all_windows if not np.isnan(w)]
    
    if len(valid_windows) < 3:  # Need at least 3 samples for meaningful statistics
        result['z_score'] = np.nan
        result['z_score_status'] = 'insufficient_data'
        result['iqr_outlier'] = False
        result['iqr_lower_bound'] = np.nan
        result['iqr_upper_bound'] = np.nan
        result['statistical_status'] = 'insufficient_data'
        return result
    
    # Z-score calculation
    mean_window = np.mean(valid_windows)
    std_window = np.std(valid_windows, ddof=1)  # Sample standard deviation
    
    if std_window > 0:
        z_score = (window_size - mean_window) / std_window
        result['z_score'] = float(z_score)
        
        if abs(z_score) <= 2.0:
            result['z_score_status'] = 'normal'
        elif abs(z_score) <= 3.0:
            result['z_score_status'] = 'warning'
        else:
            result['z_score_status'] = 'abnormal'
    else:
        result['z_score'] = np.nan
        result['z_score_status'] = 'normal'  # All values are the same
    
    # IQR method
    Q1 = np.percentile(valid_windows, 25)
    Q3 = np.percentile(valid_windows, 75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    result['iqr_lower_bound'] = float(lower_bound)
    result['iqr_upper_bound'] = float(upper_bound)
    result['iqr_outlier'] = window_size < lower_bound or window_size > upper_bound
    
    # Combined statistical status
    if result['z_score_status'] == 'abnormal' or result['iqr_outlier']:
        result['statistical_status'] = 'abnormal'
    elif result['z_score_status'] == 'warning':
        result['statistical_status'] = 'warning'
    else:
        result['statistical_status'] = 'normal'
    
    return result


def theoretical_validation(window_size: float, prob: float, B: float, 
                          sigma: float, adjusted_window: float,
                          theoretical_width: Optional[float] = None) -> Dict[str, any]:
    """
    Perform theoretical validation of window size.
    
    Parameters:
    -----------
    window_size : float
        Original window size (ms)
    prob : float
        Peak probability value (0-1)
    B : float
        Baseline parameter (0-1)
    sigma : float
        Standard deviation parameter
    adjusted_window : float
        Adjusted window size (ms)
    theoretical_width : float, optional
        Theoretical expected width at 0.5 threshold (ms)
        
    Returns:
    --------
    dict
        Dictionary containing:
        - 'pbr': Peak-to-Baseline Ratio
        - 'pbr_status': 'normal', 'warning', or 'abnormal'
        - 'adjusted_window': Adjusted window size
        - 'theoretical_comparison': Comparison with theoretical width
        - 'theoretical_status': 'normal', 'warning', or 'abnormal'
        - 'theoretical_status_combined': Combined theoretical status
    """
    result = {}
    
    # PBR calculation and status
    pbr = calculate_pbr(prob, B)
    result['pbr'] = pbr
    
    if np.isnan(pbr):
        result['pbr_status'] = 'invalid'
    elif pbr >= 2.0:
        result['pbr_status'] = 'normal'
    elif pbr >= 1.5:
        result['pbr_status'] = 'warning'
    else:
        result['pbr_status'] = 'abnormal'
    
    result['adjusted_window'] = adjusted_window
    
    # Theoretical width comparison
    if theoretical_width is not None and not np.isnan(theoretical_width) and theoretical_width > 0:
        # Compare adjusted window with theoretical width
        ratio = adjusted_window / theoretical_width
        result['theoretical_ratio'] = float(ratio)
        
        # Status based on ratio (within 0.5-2.0 is considered normal)
        if 0.5 <= ratio <= 2.0:
            result['theoretical_status'] = 'normal'
        elif 0.3 <= ratio < 0.5 or 2.0 < ratio <= 3.0:
            result['theoretical_status'] = 'warning'
        else:
            result['theoretical_status'] = 'abnormal'
    else:
        result['theoretical_ratio'] = np.nan
        result['theoretical_status'] = 'insufficient_data'
    
    # Combined theoretical status
    if result['pbr_status'] == 'abnormal' or result['theoretical_status'] == 'abnormal':
        result['theoretical_status_combined'] = 'abnormal'
    elif result['pbr_status'] == 'warning' or result['theoretical_status'] == 'warning':
        result['theoretical_status_combined'] = 'warning'
    else:
        result['theoretical_status_combined'] = 'normal'
    
    return result


def combine_evaluations(statistical_result: Dict[str, any], 
                       theoretical_result: Dict[str, any]) -> Dict[str, any]:
    """
    Combine statistical and theoretical evaluations into final assessment.
    
    Parameters:
    -----------
    statistical_result : dict
        Results from statistical_validation
    theoretical_result : dict
        Results from theoretical_validation
        
    Returns:
    --------
    dict
        Dictionary containing:
        - 'window_validity': Final validity status ('valid', 'warning', 'invalid')
        - 'combined_score': Numerical score (0-3, higher is better)
        - 'recommendation': Recommendation string
    """
    result = {}
    
    stat_status = statistical_result.get('statistical_status', 'unknown')
    theo_status = theoretical_result.get('theoretical_status_combined', 'unknown')
    
    # Determine final validity
    if stat_status == 'abnormal' or theo_status == 'abnormal':
        result['window_validity'] = 'invalid'
        combined_score = 0
    elif stat_status == 'warning' or theo_status == 'warning':
        result['window_validity'] = 'warning'
        combined_score = 1
    elif stat_status == 'normal' and theo_status == 'normal':
        result['window_validity'] = 'valid'
        combined_score = 2
    else:
        result['window_validity'] = 'warning'
        combined_score = 1
    
    result['combined_score'] = combined_score
    
    # Generate recommendation
    if result['window_validity'] == 'invalid':
        result['recommendation'] = 'Window size is invalid. Visual inspection recommended. Consider excluding from analysis.'
    elif result['window_validity'] == 'warning':
        result['recommendation'] = 'Window size shows warning signs. Visual inspection recommended.'
    else:
        result['recommendation'] = 'Window size appears valid.'
    
    return result


def validate_window_size(window_size: float, prob: float, B: float, 
                        sigma: float, mu: float, all_windows: List[float],
                        fitfunc=None, popt_raw: Optional[np.ndarray] = None,
                        x_values: Optional[np.ndarray] = None,
                        y_values: Optional[np.ndarray] = None) -> Dict[str, any]:
    """
    Multi-stage validation of window size.
    
    This function performs a comprehensive validation of window size using:
    1. Statistical validation (Z-score, IQR)
    2. Theoretical validation (PBR, adjusted window, theoretical width)
    3. Combined evaluation
    
    Parameters:
    -----------
    window_size : float
        Window size to validate (ms)
    prob : float
        Peak probability value (0-1)
    B : float
        Baseline parameter (0-1)
    sigma : float
        Standard deviation parameter
    mu : float
        Mean parameter (PSS)
    all_windows : List[float]
        List of all window sizes from all subjects
    fitfunc : callable, optional
        Fitting function (required for theoretical width calculation)
    popt_raw : np.ndarray, optional
        Raw parameter array for fitfunc (required for theoretical width)
    x_values : np.ndarray, optional
        SOA values for flatness calculation
    y_values : np.ndarray, optional
        Fitted probability values for flatness calculation
        
    Returns:
    --------
    dict
        Complete validation results including:
        - Statistical validation results
        - Theoretical validation results
        - Combined evaluation
        - All intermediate calculations (PBR, adjusted window, etc.)
    """
    result = {}
    
    # Calculate intermediate metrics
    pbr = calculate_pbr(prob, B)
    adjusted_window = calculate_adjusted_window_size(window_size, prob)
    
    # Theoretical width calculation
    theoretical_width = None
    if fitfunc is not None and popt_raw is not None:
        theo_width_dict = calculate_theoretical_width(sigma, prob, B, mu, fitfunc, popt_raw)
        theoretical_width = theo_width_dict.get('width_at_0.5', np.nan)
        result['theoretical_fwhm'] = theo_width_dict.get('fwhm', np.nan)
    
    # Flatness index calculation
    flatness = np.nan
    if x_values is not None and y_values is not None:
        flatness = calculate_flatness_index(x_values, y_values, mu, sigma)
    result['flatness_index'] = flatness
    
    # Stage 1: Statistical validation
    statistical_result = statistical_validation(window_size, all_windows)
    result.update({f'stat_{k}': v for k, v in statistical_result.items()})
    
    # Stage 2: Theoretical validation
    theoretical_result = theoretical_validation(
        window_size, prob, B, sigma, adjusted_window, theoretical_width
    )
    result.update({f'theo_{k}': v for k, v in theoretical_result.items()})
    
    # Stage 3: Combined evaluation
    combined_result = combine_evaluations(statistical_result, theoretical_result)
    result.update(combined_result)
    
    # Add intermediate metrics
    result['pbr'] = pbr
    result['adjusted_window_size'] = adjusted_window
    result['theoretical_width'] = theoretical_width
    
    return result
