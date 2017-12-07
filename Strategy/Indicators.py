# encoding=utf8
from config.config import DATA_ROOT_PATH
import pandas as pd

POINT = 5


class Indicator(object):
    def __init__(self, period=None, shift=None, time=None):
        self.__period = period
        self.__shift = shift
        data = pd.read_csv('.\HistoryData\EURUSD_1H.csv')
        self.__time=time
        if period is not None:
            self.data = data[data['Time (UTC)'] <= time][-self.__period + self.__shift:-self.__shift]
        elif period is None and shift!=0:
            self.data=data[data['Time (UTC)']<time][-shift:]


class Ma(Indicator):
    def __init__(self, period=None, shift=None,time=None):
        Indicator.__init__(self, period, shift, time)

    def get_Ma(self):
        return round(self.data['Close'].mean(), POINT)


class High(Indicator):
    def __init__(self, period=None, shift=None, time=None):
        Indicator.__init__(self, period, shift, time)

    def get_High(self):
        return round(self.data['High'].max(), POINT)


class Low(Indicator):
    def __init__(self, period=None, shift=None, time=None):
        Indicator.__init__(self, period, shift, time)

    def get_Low(self):
        return round(self.data['Low'].min(), POINT)

class BarInfo(Indicator):
    def __init__(self,period=None,shift=None,time=None):
        Indicator.__init__(self,period,shift,time)

    def get_barinfo(self):
        res={}
        res['open']=self.data['Open'].values
        res['high']=self.data['High'].values
        res['close']=self.data['Close'].values
        res['low']=self.data['Low'].values
        res['time']=self.data['Time (UTC)'].values
        return res