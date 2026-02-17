#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive window size validation module for Gaussian fitting analysis.

This module provides a comprehensive validation method including:
1. Fitting goodness of fit (primary indicator)
2. Statistical validation (Z-score, IQR method)
3. Theoretical validity (PBR, auxiliary indicator)

This is a balanced approach, using standard statistical methods without arbitrary corrections.
"""

import numpy as np
from typing import Dict, List, Optional


def calculate_pbr(prob: float, B: float) -> float:
    """Calculate Peak-to-Baseline Ratio (PBR)."""
    if B <= 0 or np.isnan(B) or np.isnan(prob):
        return np.nan
    return prob / B


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


def theoretical_validation(prob: float, B: float, 
                          reduced_deviance: Optional[float] = None,
                          reduced_chi2: Optional[float] = None) -> Dict[str, any]:
    """
    Perform theoretical validation of window size.
    
    PBR is used as an auxiliary indicator. When B=0, goodness of fit is used as the primary indicator.
    
    Parameters:
    -----------
    prob : float
        Peak probability value (0-1)
    B : float
        Baseline parameter (0-1)
    reduced_deviance : float, optional
        Reduced Deviance (preferred goodness metric)
    reduced_chi2 : float, optional
        Reduced χ² (fallback if reduced_deviance is not available)
        
    Returns:
    --------
    dict
        Dictionary containing:
        - 'pbr': Peak-to-Baseline Ratio
        - 'pbr_status': 'normal', 'warning', 'abnormal', or 'not_applicable'
        - 'theoretical_status_combined': Combined theoretical status
    """
    result = {}
    
    # PBR calculation and status (only when B > 0)
    pbr = calculate_pbr(prob, B)
    result['pbr'] = pbr
    
    # When B = 0, use goodness of fit as primary indicator
    if B <= 0 or np.isnan(B):
        # Use goodness of fit as primary indicator
        if reduced_deviance is not None and not np.isnan(reduced_deviance):
            goodness_value = float(reduced_deviance)
        elif reduced_chi2 is not None and not np.isnan(reduced_chi2):
            goodness_value = float(reduced_chi2)
        else:
            goodness_value = np.nan
        
        if np.isnan(goodness_value):
            result['pbr_status'] = 'invalid'
            result['theoretical_status_combined'] = 'invalid'
        elif goodness_value <= 1.0:
            result['pbr_status'] = 'not_applicable'  # B=0 but goodness is good
            result['theoretical_status_combined'] = 'normal'  # B=0 is theoretically valid
        elif goodness_value <= 3.0:
            result['pbr_status'] = 'not_applicable'
            result['theoretical_status_combined'] = 'warning'
        else:
            result['pbr_status'] = 'not_applicable'
            result['theoretical_status_combined'] = 'abnormal'  # Poor fit
    else:
        # B > 0: Use PBR as auxiliary indicator
        if np.isnan(pbr):
            result['pbr_status'] = 'invalid'
            result['theoretical_status_combined'] = 'invalid'
        elif pbr >= 2.0:
            result['pbr_status'] = 'normal'
            result['theoretical_status_combined'] = 'normal'
        elif pbr >= 1.5:
            result['pbr_status'] = 'warning'
            result['theoretical_status_combined'] = 'warning'
        else:
            result['pbr_status'] = 'abnormal'
            result['theoretical_status_combined'] = 'abnormal'
    
    return result


def combine_evaluations_with_goodness(goodness_status: str,
                                     statistical_result: Dict[str, any], 
                                     theoretical_result: Dict[str, any]) -> Dict[str, any]:
    """
    Combine goodness of fit, statistical and theoretical evaluations into final assessment.
    
    Goodness of fit is the primary indicator. Statistical and theoretical are auxiliary.
    
    Parameters:
    -----------
    goodness_status : str
        Goodness of fit status ('valid', 'warning', 'invalid')
    statistical_result : dict
        Results from statistical_validation
    theoretical_result : dict
        Results from theoretical_validation
        
    Returns:
    --------
    dict
        Dictionary containing:
        - 'window_validity': Final validity status ('valid', 'warning', 'invalid')
        - 'combined_score': Numerical score (0-2, higher is better)
        - 'recommendation': Recommendation string
    """
    result = {}
    
    stat_status = statistical_result.get('statistical_status', 'unknown')
    theo_status = theoretical_result.get('theoretical_status_combined', 'unknown')
    
    # Map statuses to validity levels
    def map_status_to_validity(status):
        if status == 'normal' or status == 'valid':
            return 'valid'
        elif status == 'warning':
            return 'warning'
        else:
            return 'invalid'
    
    stat_validity = map_status_to_validity(stat_status)
    theo_validity = map_status_to_validity(theo_status)
    
    # Determine final validity (goodness is primary)
    if goodness_status == 'invalid':
        result['window_validity'] = 'invalid'
        combined_score = 0
    elif goodness_status == 'warning':
        # If goodness is warning, check auxiliary indicators
        if stat_validity == 'invalid' or theo_validity == 'invalid':
            result['window_validity'] = 'invalid'
            combined_score = 0
        else:
            result['window_validity'] = 'warning'
            combined_score = 1
    else:  # goodness_status == 'valid'
        # If goodness is valid, check auxiliary indicators
        if stat_validity == 'invalid' or theo_validity == 'invalid':
            result['window_validity'] = 'warning'  # Downgrade to warning
            combined_score = 1
        elif stat_validity == 'warning' or theo_validity == 'warning':
            result['window_validity'] = 'warning'
            combined_score = 1
        else:
            result['window_validity'] = 'valid'
            combined_score = 2
    
    result['combined_score'] = combined_score
    
    # Generate recommendation
    if result['window_validity'] == 'invalid':
        result['recommendation'] = 'Window size is invalid. Visual inspection recommended. Consider excluding from analysis.'
    elif result['window_validity'] == 'warning':
        result['recommendation'] = 'Window size shows warning signs. Visual inspection recommended.'
    else:
        result['recommendation'] = 'Window size appears valid.'
    
    return result


def validate_window_size_comprehensive(window_size: float, prob: float, B: float,
                                       sigma: float, mu: float, all_windows: List[float],
                                       reduced_deviance: Optional[float] = None,
                                       reduced_chi2: Optional[float] = None,
                                       fitfunc: Optional[callable] = None,
                                       popt_raw: Optional[np.ndarray] = None,
                                       x_values: Optional[np.ndarray] = None,
                                       y_values: Optional[np.ndarray] = None,
                                       observed_values: Optional[np.ndarray] = None,
                                       predicted_values: Optional[np.ndarray] = None) -> Dict[str, any]:
    """
    Comprehensive validation of window size.
    
    This function performs validation using:
    1. Fitting goodness of fit (primary indicator)
    2. Statistical validation (Z-score, IQR)
    3. Theoretical validation (PBR, auxiliary indicator)
    4. Combined evaluation
    
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
    reduced_deviance : float, optional
        Reduced Deviance (preferred goodness metric)
    reduced_chi2 : float, optional
        Reduced χ² (fallback if reduced_deviance is not available)
    fitfunc : callable, optional
        Fitting function (not used in current implementation)
    popt_raw : np.ndarray, optional
        Raw parameter array (not used in current implementation)
    x_values : np.ndarray, optional
        SOA values (not used in current implementation)
    y_values : np.ndarray, optional
        Fitted probability values (not used in current implementation)
    observed_values : np.ndarray, optional
        Observed probability values (not used in current implementation)
    predicted_values : np.ndarray, optional
        Predicted probability values (not used in current implementation)
        
    Returns:
    --------
    dict
        Complete validation results
    """
    result = {}
    
    # Stage 0: Goodness of fit evaluation (primary indicator)
    if reduced_deviance is not None and not np.isnan(reduced_deviance):
        goodness_value = float(reduced_deviance)
        goodness_metric = 'reduced_deviance'
    elif reduced_chi2 is not None and not np.isnan(reduced_chi2):
        goodness_value = float(reduced_chi2)
        goodness_metric = 'reduced_chi2'
    else:
        goodness_value = np.nan
        goodness_metric = 'none'
    
    result['goodness_metric'] = goodness_metric
    result['goodness_value'] = goodness_value
    
    if np.isnan(goodness_value):
        goodness_status = 'invalid'
    elif goodness_value <= 1.0:
        goodness_status = 'valid'
    elif goodness_value <= 3.0:
        goodness_status = 'warning'
    else:
        goodness_status = 'invalid'
    
    result['goodness_status'] = goodness_status
    
    # Stage 1: Statistical validation
    statistical_result = statistical_validation(window_size, all_windows)
    result.update({f'stat_{k}': v for k, v in statistical_result.items()})
    
    # Stage 2: Theoretical validation (PBR as auxiliary indicator)
    theoretical_result = theoretical_validation(
        prob, B, reduced_deviance, reduced_chi2
    )
    result.update({f'theo_{k}': v for k, v in theoretical_result.items()})
    
    # Stage 3: Combined evaluation
    # Primary: goodness of fit, Secondary: statistical and theoretical
    combined_result = combine_evaluations_with_goodness(
        goodness_status, statistical_result, theoretical_result
    )
    result.update(combined_result)
    
    # Add intermediate metrics
    result['pbr'] = theoretical_result.get('pbr', np.nan)
    
    return result
