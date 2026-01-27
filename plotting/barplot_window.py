import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

sns.set()
#sns.set_style('whitegrid')
sns.set_palette('gist_yarg')

from pathlib import Path

# Load custom style
style_path = Path(__file__).parent.parent / "utils" / "dsheep_white.mplstyle"
plt.style.use(str(style_path))

x = np.array(['Cooling', 'Warming'])
x_position = np.arange(len(x))

cool = np.array([483, 548, 712, 1023, 398, 622, 796, 431, 716, 490, 666])
warm = np.array([620, 999, 804, 915, 1522, 1596, 1114, 662, 699, 1076, 1449])

cool_mu = cool.mean()
warm_mu = warm.mean()
cool_sd = cool.std()
warm_sd = warm.std()

y = np.array([cool_mu, warm_mu])
e = np.array([cool_sd, warm_sd])

error_bar_set = dict(lw=2.5, capthick=2.5, capsize=15)

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
bar_width = 0.35
bars = ax.bar(x_position, y, yerr=e, width=bar_width,
              tick_label=x,
              color=['#1D77B4', '#DB5958'],
              error_kw=error_bar_set, align="center")

for bar, value, indiv_data in zip(bars, y, [cool, warm]):
    #ax.text(bar.get_x() + bar.get_width() / 2, value, str(round(value, 2)))
    print(indiv_data)
    ax.scatter([bar.get_x() + bar.get_width() / 2] * len(indiv_data), indiv_data, color='black', marker='o', s=30, alpha=0.6, zorder=5)

# グラフ表示の設定
#plt.xlabel('Time (s)', fontsize=28) #x軸の名前とフォントサイズ
plt.ylabel('Window size (50%)', fontsize=28, fontweight='bold') #y軸の名前とフォントサイズ
#plt.legend(loc='proportion of simutanious') #ラベルを右上に記載

plt.ylim([0, 1900])

plt.tick_params(labelsize=22)

plt.xticks(fontweight='bold')
plt.yticks(fontweight='bold')

plt.tight_layout() 

plt.show()
