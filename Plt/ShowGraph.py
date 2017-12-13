# encoding=utf8
import matplotlib.pyplot as plt
from DataHandler.MongoHandler import MongoHandler


class Graph(object):
    def __init__(self, Magic=None):
        self.__magic = Magic

    def show_timegraph(self):
        timeinfo = MongoHandler(magic=self.__magic).get_timeinfo()
        fig = plt.figure("Strategy Tester of %s" % self.__magic)
        ax1 = plt.subplot2grid((3, 1), (0, 0), rowspan=2)
        ax2 = plt.subplot2grid((3, 1), (2, 0))
        ax1.set_title('Balance Graph')
        ax2.set_title('Lot Graph')
        ax1.plot(timeinfo['time'], timeinfo['mount'], label='balance')
        ax1.plot(timeinfo['time'], timeinfo['max_mount'], label='max_balance')
        ax1.plot(timeinfo['time'], timeinfo['min_mount'], label='min_balance')
        ax2.bar(timeinfo['time'], timeinfo['sell_lot'], facecolor='#ff9999', width=0.2, label='buy_lot')
        ax2.bar(timeinfo['time'], timeinfo['buy_lot'], facecolor='#9999ff', width=0.2, label='sell_lot')
        ax1.legend(loc='upper left')
        ax2.legend(loc='upper left')
        plt.show()


if __name__ == '__main__':
    timeinfo = MongoHandler(magic='1').get_timeinfo()
    fig = plt.figure("Strategy Tester of 1")
    ax1 = plt.subplot2grid((3, 1), (0, 0), rowspan=2)
    ax2 = plt.subplot2grid((3, 1), (2, 0))
    ax1.set_title('Balance Graph')
    ax2.set_title('Lot Graph')
    ax1.plot(timeinfo['time'], timeinfo['mount'], label='balance')
    ax1.plot(timeinfo['time'], timeinfo['max_mount'], label='max_balance', linestyle='--')
    ax1.plot(timeinfo['time'], timeinfo['min_mount'], label='min_balance', linestyle='--')
    ax2.bar(timeinfo['time'], timeinfo['sell_lot'], facecolor='#ff9999', width=0.2, label='buy_lot')
    ax2.bar(timeinfo['time'], timeinfo['buy_lot'], facecolor='#9999ff', width=0.2, label='sell_lot')
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper left')
    plt.show()
