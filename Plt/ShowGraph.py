import matplotlib.pyplot as plt
from DataHandler.MongoHandler import MongoHandler

class Graph(object):
    def __init__(self,Magic=None):
        self.__magic=Magic

    def show_timegraph(self):
        timeinfo = MongoHandler(magic=self.__magic).get_timeinfo()
        fig=plt.figure()
        ax1 = fig.add_subplot(2, 1, 1)
        ax2 = fig.add_subplot(2, 1, 2)
        ax1.plot(timeinfo['time'], timeinfo['mount'])
        ax1.plot(timeinfo['time'], timeinfo['max_mount'])
        ax1.plot(timeinfo['time'], timeinfo['min_mount'])
        ax2.bar(timeinfo['time'],timeinfo['sell_lot'],facecolor='#ff9999',width=0.1)
        ax2.bar(timeinfo['time'], timeinfo['buy_lot'], facecolor='#9999ff',width=0.1)
        plt.show()

if __name__ == '__main__':
   timeinfo=MongoHandler(magic='1232525').get_timeinfo()
   fig = plt.figure()
   ax1 = fig.add_subplot(2, 1, 1)
   ax2 = fig.add_subplot(2, 1, 2)
   ax1.plot(timeinfo['time'], timeinfo['mount'])
   ax1.plot(timeinfo['time'], timeinfo['max_mount'])
   ax1.plot(timeinfo['time'], timeinfo['min_mount'])
   ax2.bar(timeinfo['time'], timeinfo['sell_lot'], facecolor='#ff9999',width=0.2)
   ax2.bar(timeinfo['time'], timeinfo['buy_lot'], facecolor='#9999ff',width=0.2)
   plt.show()
