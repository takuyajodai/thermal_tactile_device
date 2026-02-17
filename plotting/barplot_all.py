import sys
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats
import pandas as pd

from pathlib import Path

# Load custom style
style_path = Path(__file__).parent.parent / "utils" / "dsheep_white.mplstyle"
plt.style.use(str(style_path))

sns.set()
#sns.set_style('whitegrid')
sns.set_palette('gist_yarg')

# CSVパス: 引数で3つ指定されていればそれを使用、なければファイルダイアログ
if len(sys.argv) >= 4:
    warm_csv_path = sys.argv[1]
    cold_csv_path = sys.argv[2]
    spatial_cold_csv_path = sys.argv[3]
else:
    from tkinter import filedialog
    warm_csv_path = filedialog.askopenfilename(
        title="Select warm data CSV file",
        filetypes=(("CSV files", "*.csv"), ("All files", "*")),
    )
    if not warm_csv_path:
        raise SystemExit("WarmデータのCSVファイルが選択されませんでした。")
    cold_csv_path = filedialog.askopenfilename(
        title="Select cold data CSV file",
        filetypes=(("CSV files", "*.csv"), ("All files", "*")),
    )
    if not cold_csv_path:
        raise SystemExit("ColdデータのCSVファイルが選択されませんでした。")
    spatial_cold_csv_path = filedialog.askopenfilename(
        title="Select spatial cold data CSV file",
        filetypes=(("CSV files", "*.csv"), ("All files", "*")),
    )
    if not spatial_cold_csv_path:
        raise SystemExit("Spatial coldデータのCSVファイルが選択されませんでした。")

# CSVファイルを読み込む（エンコーディングを自動検出）
try:
    df_warm = pd.read_csv(warm_csv_path, encoding="utf-8-sig")
except UnicodeDecodeError:
    df_warm = pd.read_csv(warm_csv_path, encoding="cp932")

try:
    df_cold = pd.read_csv(cold_csv_path, encoding="utf-8-sig")
except UnicodeDecodeError:
    df_cold = pd.read_csv(cold_csv_path, encoding="cp932")

try:
    df_spatial_cold = pd.read_csv(spatial_cold_csv_path, encoding="utf-8-sig")
except UnicodeDecodeError:
    df_spatial_cold = pd.read_csv(spatial_cold_csv_path, encoding="cp932")

# 列名の前後空白を除去（CSVによっては空白が含まれる場合がある）
for df, name in [(df_warm, "warm"), (df_cold, "cold"), (df_spatial_cold, "spatial_cold")]:
    df.columns = df.columns.str.strip()

_REQUIRED = ["PSS", "Window_size", "Prob"]


def _ensure_columns(df, path_label, path_value):
    missing = [c for c in _REQUIRED if c not in df.columns]
    if missing:
        raise SystemExit(
            f"{path_label} に必要な列がありません。\n"
            f"必要な列: {_REQUIRED}\n"
            f"実際の列: {list(df.columns)}\n"
            f"ファイル: {path_value}\n"
            "※ spatial cold には「サマリーCSV」（PSS, Window_size, Prob を含む）を指定してください。"
        )


_ensure_columns(df_warm, "Warm CSV", warm_csv_path)
_ensure_columns(df_cold, "Cold CSV", cold_csv_path)
_ensure_columns(df_spatial_cold, "Spatial cold CSV", spatial_cold_csv_path)

# データを配列に変換（NaN値を除外）
# CSVファイルには Subject, PSS, Window_size, Prob の列があると仮定
pss_w = df_warm["PSS"].dropna().values
pss_c = df_cold["PSS"].dropna().values
pss_sc = df_spatial_cold["PSS"].dropna().values

window_w = df_warm["Window_size"].dropna().values
window_c = df_cold["Window_size"].dropna().values
window_sc = df_spatial_cold["Window_size"].dropna().values

prob_w = df_warm["Prob"].dropna().values
prob_c = df_cold["Prob"].dropna().values
prob_sc = df_spatial_cold["Prob"].dropna().values

pss_c_mu = pss_c.mean()
print("pss_c_mu", pss_c_mu)
pss_w_mu = pss_w.mean()
print("pss_w_mu", pss_w_mu)
pss_sc_mu = pss_sc.mean()
print("pss_sc_mu", pss_sc_mu)
pss_c_se = stats.sem(pss_c)
print("pss_c_se", pss_c_se)
pss_w_se = stats.sem(pss_w)
print("pss_w_se", pss_w_se)
pss_sc_se = stats.sem(pss_sc)
print("pss_sc_se", pss_sc_se)

window_c_mu = window_c.mean()
print("window_c_mu", window_c_mu)
window_w_mu = window_w.mean()
print("window_w_mu", window_w_mu)
window_sc_mu = window_sc.mean()
print("window_sc_mu", window_sc_mu)
window_c_se = stats.sem(window_c)
print("window_c_se", window_c_se)
window_w_se = stats.sem(window_w)
print("window_w_se", window_w_se)
window_sc_se = stats.sem(window_sc)
print("window_sc_se", window_sc_se)

prob_c_mu = prob_c.mean()
print("prob_c_mu", prob_c_mu)
prob_w_mu = prob_w.mean()
print("prob_w_mu", prob_w_mu)
prob_sc_mu = prob_sc.mean()
print("prob_sc_mu", prob_sc_mu)
prob_c_se = stats.sem(prob_c)
prob_w_se = stats.sem(prob_w)
prob_sc_se = stats.sem(prob_sc)

#軸設定
x = np.array(['warm\nstimuli', 'cold\nstimuli', 'spatial\ncold'])
x_position = np.arange(len(x))
pss_y = np.array([pss_w_mu, pss_c_mu, pss_sc_mu])
pss_e = np.array([pss_w_se, pss_c_se, pss_sc_se])

window_y = np.array([window_w_mu, window_c_mu, window_sc_mu])
window_e = np.array([window_w_se, window_c_se, window_sc_se])

prob_y = np.array([prob_w_mu, prob_c_mu, prob_sc_mu])
prob_e = np.array([prob_w_se, prob_c_se, prob_sc_se])

error_bar_set = dict(lw=2.5, capthick=2.5, capsize=15)

#fig = plt.figure()
fig = plt.figure(figsize=(15, 5))

ax_pss = fig.add_subplot(1, 3, 1)
ax_window = fig.add_subplot(1, 3, 2)
ax_prob = fig.add_subplot(1, 3, 3)
bar_width = 0.75

# バープロットの描画
bars_pss = ax_pss.bar(x_position, pss_y, yerr=pss_e, width=bar_width,
              tick_label=x,
              color=['#DB5958', '#1D77B4', '#45B28B'],
              error_kw=error_bar_set, align="center")

bars_window = ax_window.bar(x_position, window_y, yerr=window_e, width=bar_width,
              tick_label=x,
              color=['#DB5958', '#1D77B4', '#45B28B'],
              error_kw=error_bar_set, align="center")

bars_prob = ax_prob.bar(x_position, prob_y, yerr=prob_e, width=bar_width,
              tick_label=x,
              color=['#DB5958', '#1D77B4', '#45B28B'],
              error_kw=error_bar_set, align="center")

# 個人データのプロット散布と線で接続
# warm、cold、spatial_coldのデータ数が異なる場合に対応
min_len_pss = min(len(pss_w), len(pss_c), len(pss_sc))
for i in range(min_len_pss):
    x_jitter = np.random.uniform(-0.2, 0.2)
    ax_pss.scatter(x_position[0] + x_jitter, pss_w[i], color='black', marker='o', s=30, alpha=0.4, zorder=5, clip_on=False)
    ax_pss.scatter(x_position[1] + x_jitter, pss_c[i], color='black', marker='o', s=30, alpha=0.4, zorder=5, clip_on=False)
    ax_pss.scatter(x_position[2] + x_jitter, pss_sc[i], color='black', marker='o', s=30, alpha=0.4, zorder=5, clip_on=False)
# 残りのデータがある場合
for i in range(min_len_pss, len(pss_w)):
    x_jitter = np.random.uniform(-0.2, 0.2)
    ax_pss.scatter(x_position[0] + x_jitter, pss_w[i], color='black', marker='o', s=30, alpha=0.4, zorder=5, clip_on=False)
for i in range(min_len_pss, len(pss_c)):
    x_jitter = np.random.uniform(-0.2, 0.2)
    ax_pss.scatter(x_position[1] + x_jitter, pss_c[i], color='black', marker='o', s=30, alpha=0.4, zorder=5, clip_on=False)
for i in range(min_len_pss, len(pss_sc)):
    x_jitter = np.random.uniform(-0.2, 0.2)
    ax_pss.scatter(x_position[2] + x_jitter, pss_sc[i], color='black', marker='o', s=30, alpha=0.4, zorder=5, clip_on=False)

min_len_window = min(len(window_w), len(window_c), len(window_sc))
for i in range(min_len_window):
    x_jitter = np.random.uniform(-0.2, 0.2)
    ax_window.scatter(x_position[0] + x_jitter, window_w[i], color='black', marker='o', s=30, alpha=0.4, zorder=5, clip_on=False)
    ax_window.scatter(x_position[1] + x_jitter, window_c[i], color='black', marker='o', s=30, alpha=0.4, zorder=5, clip_on=False)
    ax_window.scatter(x_position[2] + x_jitter, window_sc[i], color='black', marker='o', s=30, alpha=0.4, zorder=5, clip_on=False)
# 残りのデータがある場合
for i in range(min_len_window, len(window_w)):
    x_jitter = np.random.uniform(-0.2, 0.2)
    ax_window.scatter(x_position[0] + x_jitter, window_w[i], color='black', marker='o', s=30, alpha=0.4, zorder=5, clip_on=False)
for i in range(min_len_window, len(window_c)):
    x_jitter = np.random.uniform(-0.2, 0.2)
    ax_window.scatter(x_position[1] + x_jitter, window_c[i], color='black', marker='o', s=30, alpha=0.4, zorder=5, clip_on=False)
for i in range(min_len_window, len(window_sc)):
    x_jitter = np.random.uniform(-0.2, 0.2)
    ax_window.scatter(x_position[2] + x_jitter, window_sc[i], color='black', marker='o', s=30, alpha=0.4, zorder=5, clip_on=False)

min_len_prob = min(len(prob_w), len(prob_c), len(prob_sc))
for i in range(min_len_prob):
    x_jitter = np.random.uniform(-0.2, 0.2)
    ax_prob.scatter(x_position[0] + x_jitter, prob_w[i], color='black', marker='o', s=30, alpha=0.4, zorder=5, clip_on=False)
    ax_prob.scatter(x_position[1] + x_jitter, prob_c[i], color='black', marker='o', s=30, alpha=0.4, zorder=5, clip_on=False)
    ax_prob.scatter(x_position[2] + x_jitter, prob_sc[i], color='black', marker='o', s=30, alpha=0.4, zorder=5, clip_on=False)
# 残りのデータがある場合
for i in range(min_len_prob, len(prob_w)):
    x_jitter = np.random.uniform(-0.2, 0.2)
    ax_prob.scatter(x_position[0] + x_jitter, prob_w[i], color='black', marker='o', s=30, alpha=0.4, zorder=5, clip_on=False)
for i in range(min_len_prob, len(prob_c)):
    x_jitter = np.random.uniform(-0.2, 0.2)
    ax_prob.scatter(x_position[1] + x_jitter, prob_c[i], color='black', marker='o', s=30, alpha=0.4, zorder=5, clip_on=False)
for i in range(min_len_prob, len(prob_sc)):
    x_jitter = np.random.uniform(-0.2, 0.2)
    ax_prob.scatter(x_position[2] + x_jitter, prob_sc[i], color='black', marker='o', s=30, alpha=0.4, zorder=5, clip_on=False)


#個人データのプロット散布
"""
for bar, value, indiv_data in zip(bars, pss_y, [pss_w, pss_c]):
    #ax.text(bar.get_x() + bar.get_width() / 2, value, str(round(value, 2)))
    print(indiv_data)
    ax_pss.scatter([bar.get_x() + bar.get_width() / 2] * len(indiv_data), indiv_data, color='black', marker='o', s=30, alpha=0.6, zorder=5)

for bar, value, indiv_data in zip(bars, window_y, [window_w, window_c]):
    print(indiv_data)
    ax_window.scatter([bar.get_x() + bar.get_width() / 2] * len(indiv_data), indiv_data, color='black', marker='o', s=30, alpha=0.6, zorder=5)

for bar, value, indiv_data in zip(bars, prob_y, [prob_w, prob_c]):
    print(indiv_data)
    ax_prob.scatter([bar.get_x() + bar.get_width() / 2] * len(indiv_data), indiv_data, color='black', marker='o', s=30, alpha=0.6, zorder=5)

"""

# グラフ表示の設定

# ax_pssの設定
ax_pss.set_ylabel('PSS (ms)', fontsize=22, fontweight='bold', color='black')
ax_pss.set_ylim(-1000, 0)
ax_pss.tick_params(labelsize=15, axis='x', pad=10, colors='black')
ax_pss.tick_params(labelsize=15, axis='y', pad=10, colors='black')
ax_pss.spines['left'].set_linewidth(2)
ax_pss.spines['left'].set_color('black')
ax_pss.spines['top'].set_linewidth(2)  # 'top'のspineも太くして、色を黒に
ax_pss.spines['top'].set_color('black')


# ax_windowの設定
ax_window.set_ylabel("Window width (ms)", fontsize=22, fontweight='bold', color='black')
ax_window.set_ylim(0, 1600)
ax_window.tick_params(labelsize=15, axis='x', pad=10, colors='black')
ax_window.tick_params(labelsize=15, axis='y', pad=10, colors='black')
ax_window.spines['bottom'].set_linewidth(2)
ax_window.spines['bottom'].set_color('black')
ax_window.spines['left'].set_linewidth(2)
ax_window.spines['left'].set_color('black')

# ax_probの設定
ax_prob.set_ylabel("Proportion of\nsimultaneity judgments", fontsize=20, fontweight='bold', color='black')
ax_prob.set_ylim(0, 1)
ax_prob.tick_params(labelsize=15, axis='x', pad=10, colors='black')
ax_prob.tick_params(labelsize=15, axis='y', pad=10, colors='black')
ax_prob.spines['bottom'].set_linewidth(2)
ax_prob.spines['bottom'].set_color('black')
ax_prob.spines['left'].set_linewidth(2)
ax_prob.spines['left'].set_color('black')

for label in ax_pss.get_xticklabels() + ax_pss.get_yticklabels():
    label.set_fontweight('bold')

for label in ax_window.get_xticklabels() + ax_window.get_yticklabels():
    label.set_fontweight('bold')

for label in ax_prob.get_xticklabels() + ax_prob.get_yticklabels():
    label.set_fontweight('bold')


fig.tight_layout() 
fig.subplots_adjust(top=0.86)  # 上部に余白を設ける
# グラフの外にテキストを配置
fig.text(0.02, 0.98, '(a)', fontsize=26, fontweight = 'bold', verticalalignment='top', horizontalalignment='center')
fig.text(0.355, 0.98, '(b)', fontsize=26, fontweight = 'bold', verticalalignment='top', horizontalalignment='center')
fig.text(0.69, 0.98, '(c)', fontsize=26, fontweight = 'bold', verticalalignment='top', horizontalalignment='center')

plt.show()


plt.show()

plt.show()




