#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple window size validation module for Gaussian fitting analysis.

This module provides a simple validation method using only:
1. Fitting goodness of fit (Reduced Deviance or Reduced χ²)
2. Z-score for window size

This is the simplest approach, focusing on fitting quality and statistical outliers.
"""

import numpy as np
from typing import Dict, List, Optional


def validate_window_size_simple(window_size: float, 
                                reduced_deviance: Optional[float] = None,
                                reduced_chi2: Optional[float] = None,
                                all_windows: Optional[List[float]] = None) -> Dict[str, any]:
    """
    Simple window size validation based on fitting goodness and Z-score.
    
    This is the simplest validation method, using only:
    - Fitting goodness of fit (Reduced Deviance preferred, or Reduced χ²)
    - Z-score for window size (if all_windows is provided)
    
    Parameters:
    -----------
    window_size : float
        Window size to validate (ms)
    reduced_deviance : float, optional
        Reduced Deviance (preferred goodness metric)
    reduced_chi2 : float, optional
        Reduced χ² (fallback if reduced_deviance is not available)
    all_windows : List[float], optional
        List of all window sizes from all subjects (required for Z-score)
        
    Returns:
    --------
    dict
        Dictionary containing:
        - 'goodness_metric': Name of the goodness metric used ('reduced_deviance', 'reduced_chi2', or 'none')
        - 'goodness_value': Value of the goodness metric
        - 'goodness_status': 'valid', 'warning', or 'invalid'
        - 'z_score': Z-score value (if all_windows provided)
        - 'z_score_status': 'valid', 'warning', 'invalid', or 'insufficient_data'
        - 'window_validity': Final validity status ('valid', 'warning', 'invalid')
    """
    result = {}
    
    # =====================================================================
    # Step 1: Fitting goodness evaluation
    # =====================================================================
    # Prefer Reduced Deviance, fallback to Reduced χ²
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
    
    # Evaluate goodness (1.0 is ideal, closer to 1.0 is better)
    if np.isnan(goodness_value):
        goodness_status = 'invalid'
    elif goodness_value <= 1.0:
        goodness_status = 'valid'  # Good fit
    elif goodness_value <= 3.0:
        goodness_status = 'warning'  # Acceptable but could be improved
    else:
        goodness_status = 'invalid'  # Poor fit
    
    result['goodness_status'] = goodness_status
    
    # =====================================================================
    # Step 2: Z-score evaluation (if all_windows provided)
    # =====================================================================
    if all_windows is not None and len(all_windows) > 0:
        # Filter out NaN values
        valid_windows = [w for w in all_windows if not np.isnan(w)]
        
        if len(valid_windows) >= 3:  # Need at least 3 samples for meaningful statistics
            mean_w = np.mean(valid_windows)
            std_w = np.std(valid_windows, ddof=1)  # Sample standard deviation
            
            if std_w > 0:
                z_score = (window_size - mean_w) / std_w
                result['z_score'] = float(z_score)
                
                # Evaluate Z-score
                if abs(z_score) <= 2.0:
                    z_score_status = 'valid'
                elif abs(z_score) <= 3.0:
                    z_score_status = 'warning'
                else:
                    z_score_status = 'invalid'
            else:
                result['z_score'] = np.nan
                z_score_status = 'valid'  # All values are the same
        else:
            result['z_score'] = np.nan
            z_score_status = 'insufficient_data'
    else:
        result['z_score'] = np.nan
        z_score_status = 'insufficient_data'
    
    result['z_score_status'] = z_score_status
    
    # =====================================================================
    # Step 3: Combined evaluation
    # =====================================================================
    # If Z-score is not available, use only goodness
    if z_score_status == 'insufficient_data':
        window_validity = goodness_status
    else:
        # Both goodness and Z-score are available
        if goodness_status == 'invalid' or z_score_status == 'invalid':
            window_validity = 'invalid'
        elif goodness_status == 'warning' or z_score_status == 'warning':
            window_validity = 'warning'
        else:
            window_validity = 'valid'
    
    result['window_validity'] = window_validity
    
    return result
