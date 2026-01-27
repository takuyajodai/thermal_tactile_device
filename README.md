# HoLab - Thermal-Tactile Simultaneity Judgment Analysis

このリポジトリは、温度刺激と触覚刺激の同時性判断（TOJ: Temporal Order Judgment）実験のデータ収集と解析を行うためのツールセットです。

## プロジェクト構成

```
HoLab/
├── experiments/          # 実験実行用スクリプト（DAQ制御、刺激提示）
│   ├── thermal_tactile_isolateio_cold_spatial.py
│   ├── thermal_tactile_isolateio_cold.py
│   ├── thermal_tactile_isolateaio_warm.py
│   ├── thermal_tactile_isolateaio.py
│   ├── caio.py          # CONTEC AIOライブラリ（DAQ制御）
│   └── SOA_generator.py # SOA（Stimulus Onset Asynchrony）リスト生成
├── analysis/            # データ解析スクリプト
│   ├── aggregate_answers.py              # 回答CSVファイルの集約
│   ├── Gaussian_fitting_integrate_cold.py
│   ├── Gaussian_fitting_integrate_spatial_cold.py
│   └── Gaussian_fitting_integrate_warm.py
├── plotting/           # 可視化スクリプト
│   ├── barplot_all.py
│   ├── barplot_spatial_cold.py
│   └── barplot_window.py
├── utils/              # 共通ユーティリティ
│   ├── dsheep_white.mplstyle  # matplotlibスタイル
│   └── plot.py                # リアルタイムプロット用クラス
└── data/               # データディレクトリ
    └── sample/          # サンプルデータ（リポジトリに含める）
```

## セットアップ

### 必要な環境

- Python 3.8以上
- Windows（実験スクリプトはWindows専用、CONTEC AIOライブラリが必要）

### インストール

1. リポジトリをクローン:
```bash
git clone <repository-url>
cd HoLab
```

2. 依存パッケージをインストール:
```bash
pip install -r requirements.txt
```

3. tkinterの確認:
   - macOS/Linux: `sudo apt-get install python3-tk` (必要に応じて)
   - Windows: Pythonに含まれています

4. CONTEC AIOライブラリ（実験実行時のみ必要）:
   - CONTEC社のAPI-AIO(WDM)ドライバをインストール
   - `caio.py`を適切な場所に配置

## 使い方

### データ解析

#### 1. 回答データの集約

複数の被験者データを集約します:

```bash
# ファイル選択ダイアログが開きます
python analysis/aggregate_answers.py

# または、コマンドライン引数で指定
python analysis/aggregate_answers.py path/to/*_answer.csv -o output.csv
```

入力ファイル名の形式: `[index]_[subject]_[run]_answer.csv`

#### 2. ガウシアンフィッティング

各条件（cold, warm, spatial_cold）に対して、ガウシアン関数でフィッティングを行い、PSS（Point of Subjective Simultaneity）やWindow sizeを計算します:

```bash
# Cold条件
python analysis/Gaussian_fitting_integrate_cold.py

# Warm条件
python analysis/Gaussian_fitting_integrate_warm.py

# Spatial Cold条件
python analysis/Gaussian_fitting_integrate_spatial_cold.py
```

実行すると:
1. ファイル選択ダイアログが開きます（複数選択可）
2. 各被験者データと集約データに対してフィッティングを実行
3. グラフが表示されます
4. 結果をCSVファイルとして保存するダイアログが開きます

**出力される指標**:
- PSS: 主観的同時点（ms）
- Window_size: 50%閾値の幅（ms）
- Prob: ピークの確率値
- Reduced_chi_squared: 正規化されたカイ二乗値
- AIC/BIC: モデル選択指標（spatial_coldのみ）
- Reduced_deviance: 正規化されたデビアンス（spatial_coldのみ）

#### 3. 可視化

```bash
# 全条件の比較
python plotting/barplot_all.py

# Spatial Cold条件
python plotting/barplot_spatial_cold.py

# Window sizeの比較
python plotting/barplot_window.py
```

### 実験実行

実験スクリプトはWindows環境でCONTEC AIOデバイスが必要です。

1. `SOA_generator.py`でSOAリストを設定
2. 対応する実験スクリプトを実行:
   - `thermal_tactile_isolateio_cold_spatial.py`: 空間的寒冷刺激
   - `thermal_tactile_isolateio_cold.py`: 寒冷刺激
   - `thermal_tactile_isolateaio_warm.py`: 温熱刺激
   - `thermal_tactile_isolateaio.py`: 汎用

## データ形式

### 入力CSV形式

解析スクリプトは以下の形式のCSVを想定しています:

- ヘッダー行が必要
- SOA列: 刺激間隔（ms）
- 回答列（列5）: 0（非同時性）または1（同時性）

### 出力CSV形式

解析結果は以下の列を含みます:

- Subject: 被験者ID
- PSS: 主観的同時点（ms）
- Window_size: 50%閾値の幅（ms）
- Prob: ピークの確率値
- Reduced_chi_squared: 正規化されたカイ二乗値
- （spatial_coldのみ）AIC, BIC, Reduced_deviance

## 注意事項

- 生成された画像（`*.png`）や集約CSV（`aggregated.csv`）は`.gitignore`で除外されています
- 本番データ（`cold_data/`, `warm_data/`）はリポジトリに含まれていません
- サンプルデータは`data/sample/`に配置してください

## ライセンス

[ライセンス情報を記載]

## 著者

jodaitakuya
