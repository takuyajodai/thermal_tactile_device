import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats
from tkinter import filedialog
import pandas as pd

sns.set()
#sns.set_style('whitegrid')
sns.set_palette('gist_yarg')

from pathlib import Path

# Load custom style
style_path = Path(__file__).parent.parent / "utils" / "dsheep_white.mplstyle"
plt.style.use(str(style_path))

# CSVファイルからデータを読み込む
# Spatial coldデータのCSVファイルを選択
spatial_cold_csv_path = filedialog.askopenfilename(
    title="Select spatial cold data CSV file",
    filetypes=(("CSV files", "*.csv"), ("All files", "*")),
)
if not spatial_cold_csv_path:
    raise SystemExit("Spatial coldデータのCSVファイルが選択されませんでした。")

# CSVファイルを読み込む（エンコーディングを自動検出）
try:
    df = pd.read_csv(spatial_cold_csv_path, encoding="utf-8-sig")
except UnicodeDecodeError:
    df = pd.read_csv(spatial_cold_csv_path, encoding="cp932")

# データを配列に変換（NaN値を除外）
# CSVファイルには Subject, PSS, Window_size, Prob の列があると仮定
pss = df["PSS"].dropna().values
window = df["Window_size"].dropna().values
prob = df["Prob"].dropna().values

# 統計値の計算
pss_mu = pss.mean()
print("pss_mu", pss_mu)
pss_se = stats.sem(pss)
print("pss_se", pss_se)

window_mu = window.mean()
print("window_mu", window_mu)
window_se = stats.sem(window)
print("window_se", window_se)

prob_mu = prob.mean()
print("prob_mu", prob_mu)
prob_se = stats.sem(prob)
print("prob_se", prob_se)

# 軸設定（単一のバーを表示するため、ダミーのx軸を使用）
x_position = np.array([0])
pss_y = np.array([pss_mu])
pss_e = np.array([pss_se])

window_y = np.array([window_mu])
window_e = np.array([window_se])

prob_y = np.array([prob_mu])
prob_e = np.array([prob_se])

error_bar_set = dict(lw=2.5, capthick=2.5, capsize=15)

#fig = plt.figure()
fig = plt.figure(figsize=(15, 5))

ax_pss = fig.add_subplot(1, 3, 1)
ax_window = fig.add_subplot(1, 3, 2)
ax_prob = fig.add_subplot(1, 3, 3)
bar_width = 0.75

# バープロットの描画
bars_pss = ax_pss.bar(x_position, pss_y, yerr=pss_e, width=bar_width,
              color=['#1D77B4'],
              error_kw=error_bar_set, align="center")

bars_window = ax_window.bar(x_position, window_y, yerr=window_e, width=bar_width,
              color=['#1D77B4'],
              error_kw=error_bar_set, align="center")

bars_prob = ax_prob.bar(x_position, prob_y, yerr=prob_e, width=bar_width,
              color=['#1D77B4'],
              error_kw=error_bar_set, align="center")

# 個人データのプロット散布
for i in range(len(pss)):
    x_jitter = np.random.uniform(-0.2, 0.2)
    ax_pss.scatter(x_position[0] + x_jitter, pss[i], color='black', marker='o', s=30, alpha=0.4, zorder=5, clip_on=False)

for i in range(len(window)):
    x_jitter = np.random.uniform(-0.2, 0.2)
    ax_window.scatter(x_position[0] + x_jitter, window[i], color='black', marker='o', s=30, alpha=0.4, zorder=5, clip_on=False)

for i in range(len(prob)):
    x_jitter = np.random.uniform(-0.2, 0.2)
    ax_prob.scatter(x_position[0] + x_jitter, prob[i], color='black', marker='o', s=30, alpha=0.4, zorder=5, clip_on=False)


# グラフ表示の設定

# ax_pssの設定
ax_pss.set_ylabel('PSS (ms)', fontsize=22, fontweight='bold', color='black')
ax_pss.set_xlabel('Spatial cold', fontsize=18, fontweight='bold', color='black')
ax_pss.set_ylim(-1000, 0)
ax_pss.set_xticks([])  # x軸の目盛りを非表示
ax_pss.tick_params(labelsize=15, axis='y', pad=10, colors='black')
ax_pss.spines['left'].set_linewidth(2)
ax_pss.spines['left'].set_color('black')
ax_pss.spines['top'].set_linewidth(2)  # 'top'のspineも太くして、色を黒に
ax_pss.spines['top'].set_color('black')
ax_pss.spines['bottom'].set_linewidth(2)
ax_pss.spines['bottom'].set_color('black')
ax_pss.spines['right'].set_visible(False)


# ax_windowの設定
ax_window.set_ylabel("Window width (ms)", fontsize=22, fontweight='bold', color='black')
ax_window.set_xlabel('Spatial cold', fontsize=18, fontweight='bold', color='black')
ax_window.set_ylim(0, 1600)
ax_window.set_xticks([])  # x軸の目盛りを非表示
ax_window.tick_params(labelsize=15, axis='y', pad=10, colors='black')
ax_window.spines['bottom'].set_linewidth(2)
ax_window.spines['bottom'].set_color('black')
ax_window.spines['left'].set_linewidth(2)
ax_window.spines['left'].set_color('black')
ax_window.spines['top'].set_visible(False)
ax_window.spines['right'].set_visible(False)

# ax_probの設定
ax_prob.set_ylabel("Proportion of\nsimultaneity judgments", fontsize=20, fontweight='bold', color='black')
ax_prob.set_xlabel('Spatial cold', fontsize=18, fontweight='bold', color='black')
ax_prob.set_ylim(0, 1)
ax_prob.set_xticks([])  # x軸の目盛りを非表示
ax_prob.tick_params(labelsize=15, axis='y', pad=10, colors='black')
ax_prob.spines['bottom'].set_linewidth(2)
ax_prob.spines['bottom'].set_color('black')
ax_prob.spines['left'].set_linewidth(2)
ax_prob.spines['left'].set_color('black')
ax_prob.spines['top'].set_visible(False)
ax_prob.spines['right'].set_visible(False)

for label in ax_pss.get_yticklabels():
    label.set_fontweight('bold')

for label in ax_window.get_yticklabels():
    label.set_fontweight('bold')

for label in ax_prob.get_yticklabels():
    label.set_fontweight('bold')


fig.tight_layout() 
fig.subplots_adjust(top=0.86)  # 上部に余白を設ける
# グラフの外にテキストを配置
fig.text(0.02, 0.98, '(a)', fontsize=26, fontweight = 'bold', verticalalignment='top', horizontalalignment='center')
fig.text(0.355, 0.98, '(b)', fontsize=26, fontweight = 'bold', verticalalignment='top', horizontalalignment='center')
fig.text(0.69, 0.98, '(c)', fontsize=26, fontweight = 'bold', verticalalignment='top', horizontalalignment='center')

plt.show()

