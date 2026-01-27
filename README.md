# Thermal-Tactile Simultaneity Judgment Analysis

This repository contains a toolset for data collection and analysis of temporal order judgment (TOJ) experiments involving thermal and tactile stimuli.

## Project Structure

```
thermal_tactile_device/
├── experiments/          # Experimental scripts (DAQ control, stimulus presentation)
│   ├── thermal_tactile_isolateio_cold_spatial.py
│   ├── thermal_tactile_isolateio_cold.py
│   ├── thermal_tactile_isolateaio_warm.py
│   ├── thermal_tactile_isolateaio.py
│   ├── caio.py          # CONTEC AIO library (DAQ control)
│   └── SOA_generator.py # SOA (Stimulus Onset Asynchrony) list generator
├── analysis/            # Data analysis scripts
│   ├── aggregate_answers.py              # Aggregate answer CSV files
│   ├── Gaussian_fitting_integrate_cold.py
│   ├── Gaussian_fitting_integrate_spatial_cold.py
│   └── Gaussian_fitting_integrate_warm.py
├── plotting/           # Visualization scripts
│   ├── barplot_all.py
│   ├── barplot_spatial_cold.py
│   └── barplot_window.py
├── utils/              # Common utilities
│   ├── dsheep_white.mplstyle  # matplotlib style
│   └── plot.py                # Real-time plotting class
└── data/               # Data directory
    └── sample/          # Sample data (included in repository)
```

## Setup

### Requirements

- Python 3.8 or higher
- Windows (experimental scripts are Windows-specific and require CONTEC AIO library)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/takuyajodai/thermal_tactile_device.git
cd thermal_tactile_device
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Verify tkinter:
   - macOS/Linux: `sudo apt-get install python3-tk` (if needed)
   - Windows: Included with Python

4. CONTEC AIO library (required only for running experiments):
   - Install CONTEC API-AIO(WDM) driver
   - Place `caio.py` in the appropriate location

## Usage

### Data Analysis

#### 1. Aggregate Answer Data

Aggregate data from multiple participants:

```bash
# A file selection dialog will open
python analysis/aggregate_answers.py

# Or specify via command line arguments
python analysis/aggregate_answers.py path/to/*_answer.csv -o output.csv
```

Input file name format: `[index]_[subject]_[run]_answer.csv`

#### 2. Gaussian Fitting

Perform Gaussian function fitting for each condition (cold, warm, spatial_cold) to calculate PSS (Point of Subjective Simultaneity) and Window size:

```bash
# Cold condition
python analysis/Gaussian_fitting_integrate_cold.py

# Warm condition
python analysis/Gaussian_fitting_integrate_warm.py

# Spatial Cold condition
python analysis/Gaussian_fitting_integrate_spatial_cold.py
```

When executed:
1. A file selection dialog will open (multiple selection allowed)
2. Fitting is performed for each participant's data and aggregated data
3. Graphs are displayed
4. A dialog opens to save results as a CSV file

**Output metrics**:
- PSS: Point of Subjective Simultaneity (ms)
- Window_size: Width at 50% threshold (ms)
- Prob: Peak probability value
- Reduced_chi_squared: Normalized chi-squared value
- AIC/BIC: Model selection metrics (spatial_cold only)
- Reduced_deviance: Normalized deviance (spatial_cold only)

#### 3. Visualization

```bash
# Compare all conditions
python plotting/barplot_all.py

# Spatial Cold condition
python plotting/barplot_spatial_cold.py

# Compare Window sizes
python plotting/barplot_window.py
```

### Running Experiments

Experimental scripts require Windows environment and CONTEC AIO device.

1. Set SOA list using `SOA_generator.py`
2. Run the corresponding experimental script:
   - `thermal_tactile_isolateio_cold_spatial.py`: Spatial cold thermal stimulus
   - `thermal_tactile_isolateio_cold.py`: Cold thermal stimulus
   - `thermal_tactile_isolateaio_warm.py`: Warm thermal stimulus
   - `thermal_tactile_isolateaio.py`: General purpose

## Data Format

### Input CSV Format

Analysis scripts expect CSV files in the following format:

- Header row required
- SOA column: Stimulus interval (ms)
- Answer column (column 5): 0 (non-simultaneous) or 1 (simultaneous)

### Output CSV Format

Analysis results include the following columns:

- Subject: Participant ID
- PSS: Point of Subjective Simultaneity (ms)
- Window_size: Width at 50% threshold (ms)
- Prob: Peak probability value
- Reduced_chi_squared: Normalized chi-squared value
- (spatial_cold only) AIC, BIC, Reduced_deviance

## Notes

- Generated images (`*.png`) and aggregated CSV files (`aggregated.csv`) are excluded by `.gitignore`
- Production data (`cold_data/`, `warm_data/`) have been removed from the repository and are excluded by `.gitignore`
- Sample data is located in `data/sample/`

## Related Publication

This repository contains data analysis tools related to the following publication:

Jodai, T., Jones, L. A., Terao, M., & Ho, H.-N. (2024). Perceiving Synchrony: Determining Thermal-tactile Simultaneity Windows. ResearchGate. https://www.researchgate.net/publication/383702978_Perceiving_Synchrony_Determining_Thermal-tactile_Simultaneity_Windows

## Authors

**First Author**: Takuya Jodai

**Co-authors**: 
- Lynette A. Jones
- Masahiko Terao
- Hsin-Ni Ho

The code in this repository was used in the research described in the above publication.
