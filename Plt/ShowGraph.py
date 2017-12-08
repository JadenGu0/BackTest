import matplotlib.pyplot as plt
from DataHandler.MongoHandler import MongoHandler

class Graph(object):
    def __init__(self,Magic=None):
        self.__magic=Magic

    def show_timegraph(self):
        timeinfo = MongoHandler(magic=self.__magic).get_timeinfo()
        plt.figure('time')
        plt.plot(timeinfo['time'], timeinfo['mount'])
        plt.plot(timeinfo['time'], timeinfo['max_mount'])
        plt.plot(timeinfo['time'], timeinfo['min_mount'])
        plt.show()