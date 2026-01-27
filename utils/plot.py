import numpy as np
import matplotlib.pyplot as plt
import time

class RealtimePlot1D():
    def __init__(
        self,
        length,
        xlabel="time[sec]",
        ylabel="temperature[℃]",
        title="RealtimePlot1D",
        color="r",
        marker="-",
        alpha=1.0,
        ylim=None,
        xlim=None
    ):
        self.length = length
        self.color = color
        self.marker = marker
        self.alpha = 1.0
        self.ylim = ylim
        self.xlim = xlim
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.title = title
        self.line = None

        #プロット初期化
        self.init_plot()

    def init_plot(self):
        self.x_vec = np.zeros(self.length) 
        self.y_vec = np.zeros(self.length)
        
        plt.ion()
        fig = plt.figure(figsize=(10,6))
        ax = fig.add_subplot(111)
        
        self.line = ax.plot(self.x_vec, self.y_vec, 
                            self.marker, color=self.color, 
                            alpha=self.alpha)  
        if self.ylim is not None:
            plt.ylim(self.ylim[0], self.ylim[1])
        if self.xlim is not None:
            plt.xlim(self.xlim[0], self.xlim[1])
        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)
        plt.title(self.title)
        plt.grid()

        plt.show()
        
        self.index = 0
        self.pretime = 0.0
        self.fps = 0.0

    def update_index(self):
        self.index = self.index + 1 if self.index < self.length-1 else 0
        
    def update_ylim(self, y_data):
        ylim = self.line[0].axes.get_ylim()
        if   y_data < ylim[0]:
            plt.ylim(y_data*1.1, ylim[1])
        elif y_data > ylim[1]:
            plt.ylim(ylim[0], y_data*1.4)
            
    def compute_fps(self):
        curtime = time.time()
        time_diff = curtime - self.pretime
        self.fps = 1.0 / (time_diff + 1e-16)
        self.pretime = curtime 

    def update(self, x_data, y_data):
        # プロットする配列の更新
        self.y_vec[self.index] = y_data
        
        y_pos = self.index + 1 if self.index < self.length else 0
        tmp_y_vec = np.r_[self.y_vec[y_pos:self.length], self.y_vec[0:y_pos]]
        self.line[0].set_ydata(tmp_y_vec)
        if self.ylim is None:
            self.update_ylim(y_data)
        
        self.line[0].set_xdata(x_data)
        if self.xlim is None:
            plt.xlim(min(x_data), max(x_data))

        plt.title(f"fps: {self.fps:0.1f} Hz")
        plt.pause(0.01)
        
        # 次のプロット更新のための処理
        self.update_index()
        self.compute_fps()